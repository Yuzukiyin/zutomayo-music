// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    console.log('Music Fan Site loaded!');
    
    // 随机悬停文字功能 - 支持换行显示
    const overlayTexts = document.querySelectorAll('.overlay-text');
    overlayTexts.forEach(textElement => {
        const textsData = textElement.getAttribute('data-texts');
        if (textsData) {
            const textArray = textsData.split('|'); // 用 | 分隔多组文字
            
            // 鼠标悬停时随机显示一组文字
            const imageOverlay = textElement.closest('.image-overlay');
            imageOverlay.addEventListener('mouseenter', function() {
                const randomText = textArray[Math.floor(Math.random() * textArray.length)];
                // 将 \n 替换为 <br> 标签以实现换行
                textElement.innerHTML = randomText.replace(/\n/g, '<br>');
            });
        }
    });
    
    // 为专辑卡片添加点击动画效果
    const albumCards = document.querySelectorAll('.album-card');
    albumCards.forEach(card => {
        card.addEventListener('click', function(e) {
            // 如果点击的不是按钮，则导航到专辑详情页
            if (!e.target.classList.contains('btn')) {
                const albumId = this.dataset.albumId;
                window.location.href = `/album/${albumId}`;
            }
        });
    });
    
    // 平滑滚动
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// 使用 Fetch API 获取专辑数据（示例）
async function fetchAlbums() {
    try {
        const response = await fetch('/api/albums');
        const albums = await response.json();
        console.log('专辑数据:', albums);
          return albums;
    } catch (error) {
        console.error('获取专辑数据失败:', error);
    }
}

// 获取指定专辑的曲目（示例）
async function fetchTracks(albumId) {
    try {
        const response = await fetch(`/api/album/${albumId}/tracks`);
        const tracks = await response.json();
        console.log('曲目数据:', tracks);
        return tracks;
    } catch (error) {
        console.error('获取曲目数据失败:', error);
    }
}

// 添加到收藏（示例功能）
function addToFavorites(albumId) {
    // 这里可以实现收藏功能
    console.log(`专辑 ${albumId} 已添加到收藏`);
    alert('已添加到收藏！');
}

// 分享专辑（示例功能）
function shareAlbum(albumId, albumTitle) {
    const url = window.location.origin + `/album/${albumId}`;
    const text = `来看看这张专辑：${albumTitle}`;
    
    if (navigator.share) {
        navigator.share({
            title: albumTitle,
            text: text,
            url: url
        }).catch(err => console.log('分享失败', err));
    } else {
        // 降级方案：复制链接
        navigator.clipboard.writeText(url).then(() => {
            alert('链接已复制到剪贴板！');
        });
    }
}
