// ── Tab Navigation ────────────────────────────────────────────────────────

document.querySelectorAll('.nav-links a').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const tabId = link.dataset.tab;

        document.querySelectorAll('.nav-links a').forEach(l => l.classList.remove('active'));
        link.classList.add('active');

        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.getElementById(`tab-${tabId}`).classList.add('active');

        if (tabId === 'dashboard') loadDashboard();
        if (tabId === 'auto-poster') loadFolderStatus();
        if (tabId === 'scheduled-list') loadScheduledPosts();
    });
});

// ── Loading Overlay ───────────────────────────────────────────────────────

function showLoading(text = 'Processing...') {
    document.getElementById('loading-text').textContent = text;
    document.getElementById('loading-overlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loading-overlay').style.display = 'none';
}

// ── API Helper ────────────────────────────────────────────────────────────

async function apiCall(url, options = {}) {
    const resp = await fetch(url, {
        headers: { 'Content-Type': 'application/json', ...options.headers },
        credentials: 'include',
        ...options,
    });
    const data = await resp.json();
    if (!resp.ok) {
        throw new Error(data.detail || 'API error');
    }
    return data;
}

// ── Dashboard ─────────────────────────────────────────────────────────────

async function loadDashboard() {
    try {
        const [insights, scheduled, recent] = await Promise.allSettled([
            apiCall('/api/insights'),
            apiCall('/api/scheduled'),
            apiCall('/api/recent-posts?limit=6'),
        ]);

        if (insights.status === 'fulfilled' && insights.value.success) {
            const d = insights.value.data;
            document.getElementById('stat-followers').textContent =
                (d.followers_count || 0).toLocaleString();
            document.getElementById('stat-posts').textContent =
                (d.media_count || 0).toLocaleString();
            document.getElementById('stat-username').textContent =
                `@${d.username || 'N/A'}`;
        }

        if (scheduled.status === 'fulfilled' && scheduled.value.success) {
            const pendingCount = scheduled.value.posts.filter(p => p.status === 'pending').length;
            document.getElementById('stat-scheduled').textContent = pendingCount;
        }

        if (recent.status === 'fulfilled' && recent.value.success) {
            renderRecentPosts(recent.value.posts);
        }
    } catch (err) {
        console.error('Dashboard load error:', err);
    }
}

function renderRecentPosts(posts) {
    const container = document.getElementById('recent-posts');
    if (!posts || posts.length === 0) {
        container.innerHTML = '<p class="placeholder">No recent posts found.</p>';
        return;
    }
    container.innerHTML = posts.map(post => `
        <div class="post-card">
            <div class="caption">${escapeHtml(post.caption || 'No caption')}</div>
            <div class="meta">
                <div class="engagement">
                    <span>❤️ ${post.like_count || 0}</span>
                    <span>💬 ${post.comments_count || 0}</span>
                </div>
                <span>${formatDate(post.timestamp)}</span>
            </div>
        </div>
    `).join('');
}

// ── Auto Poster ───────────────────────────────────────────────────────────

async function loadFolderStatus() {
    try {
        const data = await apiCall('/api/folder-status');
        document.getElementById('stat-unposted').textContent = data.unposted_count;
        document.getElementById('stat-total-posted').textContent = data.total_posted;

        const queuedDiv = document.getElementById('queued-files');
        if (data.unposted_files.length > 0) {
            queuedDiv.innerHTML = data.unposted_files.map(f => `
                <div class="post-card">
                    <div class="caption">${f}</div>
                    <div class="meta"><span>Queued</span></div>
                </div>
            `).join('');
        } else {
            queuedDiv.innerHTML = '<p class="placeholder">No images in queue.</p>';
        }

        const logDiv = document.getElementById('auto-post-log');
        if (data.recent_log.length > 0) {
            logDiv.innerHTML = data.recent_log.reverse().map(l => `
                <div class="post-card">
                    <div class="caption">${l.filename}</div>
                    <div class="meta">
                        <span style="color: ${l.status === 'posted' ? '#4caf50' : '#f44336'}">
                            ${l.status.toUpperCase()}
                        </span>
                        <span>${l.timestamp ? new Date(l.timestamp).toLocaleString() : ''}</span>
                    </div>
                    ${l.caption_preview ? `<div style="color: var(--text-secondary); font-size: 0.8rem; margin-top: 0.5rem;">${l.caption_preview.substring(0, 100)}...</div>` : ''}
                </div>
            `).join('');
        } else {
            logDiv.innerHTML = '<p class="placeholder">No posts yet.</p>';
        }
    } catch (err) {
        console.error('Folder status error:', err);
    }
}

document.getElementById('upload-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const input = document.getElementById('image-files');
    if (!input.files.length) return;

    showLoading('Uploading images...');
    const formData = new FormData();
    for (const file of input.files) {
        formData.append('files', file);
    }

    try {
        const resp = await fetch('/api/upload-images', {
            method: 'POST',
            credentials: 'include',
            body: formData,
        });
        const data = await resp.json();
        hideLoading();
        alert(`Uploaded ${data.total} image(s) to queue!`);
        input.value = '';
        loadFolderStatus();
    } catch (err) {
        hideLoading();
        alert('Upload failed: ' + err.message);
    }
});

document.getElementById('auto-post-now-btn').addEventListener('click', async () => {
    if (!confirm('Post the next queued image now? AI will generate the caption automatically.')) return;

    showLoading('AI is analyzing image, generating caption, and posting... This may take 2-3 minutes.');
    try {
        const data = await apiCall('/api/auto-post-now', { method: 'POST' });
        hideLoading();
        if (data.status === 'posted') {
            alert(`Posted! Image: ${data.filename}\nMedia ID: ${data.media_id}`);
        } else {
            alert(data.message || 'No images to post.');
        }
        loadFolderStatus();
    } catch (err) {
        hideLoading();
        alert('Auto-post failed: ' + err.message);
    }
});

// ── Content Generation ────────────────────────────────────────────────────

document.getElementById('generate-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('generate-btn');
    btn.disabled = true;
    const imageUrl = document.getElementById('gen-image-url').value;
    const loadingMsg = imageUrl
        ? 'AI is analyzing your image and generating professional content... This may take 2-3 minutes.'
        : 'AI agents are generating your content... This may take 1-2 minutes.';
    showLoading(loadingMsg);

    try {
        const data = await apiCall('/api/generate', {
            method: 'POST',
            body: JSON.stringify({
                topic: document.getElementById('topic').value,
                brand_voice: document.getElementById('brand-voice').value,
                target_audience: document.getElementById('target-audience').value,
                post_type: document.getElementById('post-type').value,
                num_posts: parseInt(document.getElementById('num-posts').value),
                image_url: imageUrl,
            }),
        });

        const resultDiv = document.getElementById('generate-result');
        const outputPre = document.getElementById('generate-output');
        outputPre.textContent = data.data.raw_output || JSON.stringify(data.data, null, 2);
        resultDiv.style.display = 'block';
    } catch (err) {
        alert('Error: ' + err.message);
    } finally {
        hideLoading();
        btn.disabled = false;
    }
});

// ── Schedule Post ─────────────────────────────────────────────────────────

document.getElementById('schedule-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    showLoading('Scheduling post...');

    try {
        const schedTimeInput = document.getElementById('sched-time').value;
        const scheduledTime = new Date(schedTimeInput).toISOString();

        const data = await apiCall('/api/schedule', {
            method: 'POST',
            body: JSON.stringify({
                image_url: document.getElementById('sched-image-url').value,
                caption: document.getElementById('sched-caption').value,
                hashtags: document.getElementById('sched-hashtags').value,
                scheduled_time: scheduledTime,
            }),
        });

        const resultDiv = document.getElementById('schedule-result');
        resultDiv.style.display = 'block';
        resultDiv.innerHTML = `
            <p style="color: var(--success);">✅ Post scheduled successfully!</p>
            <p>Post ID: <strong>${data.post_id}</strong></p>
            <p>Scheduled for: <strong>${formatDate(data.scheduled_time)}</strong></p>
        `;
        e.target.reset();
    } catch (err) {
        alert('Error: ' + err.message);
    } finally {
        hideLoading();
    }
});

// ── Scheduled Posts List ──────────────────────────────────────────────────

document.getElementById('refresh-scheduled').addEventListener('click', loadScheduledPosts);

async function loadScheduledPosts() {
    const container = document.getElementById('scheduled-posts-list');
    container.innerHTML = '<p class="placeholder">Loading...</p>';

    try {
        const data = await apiCall('/api/scheduled');
        if (!data.posts || data.posts.length === 0) {
            container.innerHTML = '<p class="placeholder">No scheduled posts yet.</p>';
            return;
        }
        container.innerHTML = data.posts.map(post => `
            <div class="scheduled-item">
                <div class="info">
                    <span class="status-badge status-${post.status}">${post.status}</span>
                    <div class="caption-preview">${escapeHtml((post.caption || '').substring(0, 100))}...</div>
                    <div class="time">Scheduled: ${formatDate(post.scheduled_time)}</div>
                </div>
                ${post.status === 'pending' ? `
                    <button class="btn btn-danger" onclick="cancelPost('${post.post_id}')">Cancel</button>
                ` : ''}
            </div>
        `).join('');
    } catch (err) {
        container.innerHTML = `<p class="placeholder">Error: ${err.message}</p>`;
    }
}

async function cancelPost(postId) {
    if (!confirm('Cancel this scheduled post?')) return;
    try {
        await apiCall(`/api/schedule/${postId}`, { method: 'DELETE' });
        loadScheduledPosts();
    } catch (err) {
        alert('Error: ' + err.message);
    }
}

// ── Post Now ──────────────────────────────────────────────────────────────

document.getElementById('post-now-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    showLoading('Publishing to Instagram...');

    try {
        const data = await apiCall('/api/post-now', {
            method: 'POST',
            body: JSON.stringify({
                image_url: document.getElementById('now-image-url').value,
                caption: document.getElementById('now-caption').value,
                hashtags: document.getElementById('now-hashtags').value,
            }),
        });

        const resultDiv = document.getElementById('post-now-result');
        resultDiv.style.display = 'block';
        resultDiv.innerHTML = `
            <p style="color: var(--success);">✅ Post published successfully!</p>
            <p>Media ID: <strong>${data.media_id}</strong></p>
        `;
        e.target.reset();
    } catch (err) {
        alert('Error: ' + err.message);
    } finally {
        hideLoading();
    }
});

// ── Utilities ─────────────────────────────────────────────────────────────

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateStr) {
    if (!dateStr) return 'N/A';
    try {
        return new Date(dateStr).toLocaleString();
    } catch {
        return dateStr;
    }
}

// ── Init ──────────────────────────────────────────────────────────────────

loadDashboard();
