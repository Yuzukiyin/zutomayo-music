// 播放器轮播功能
document.addEventListener('DOMContentLoaded', function() {
    const carousel = document.querySelector('.player-carousel');
    if (!carousel) return;
    
    const track = carousel.querySelector('.carousel-track');
    const items = carousel.querySelectorAll('.carousel-item');
    const prevBtn = carousel.querySelector('.carousel-btn.prev');
    const nextBtn = carousel.querySelector('.carousel-btn.next');
    const indicators = carousel.querySelectorAll('.indicator');
    
    let currentIndex = 0;
    const totalItems = items.length;
    
    if (totalItems <= 1) return; // 只有一个播放器时不需要轮播
    
    // 更新轮播位置
    function updateCarousel() {
        // 移除所有 active 类
        items.forEach(item => item.classList.remove('active'));
        indicators.forEach(ind => ind.classList.remove('active'));
        
        // 添加当前项的 active 类
        items[currentIndex].classList.add('active');
        indicators[currentIndex].classList.add('active');
        
        // 移动轮播容器
        const offset = -currentIndex * 100;
        track.style.transform = `translateX(${offset}%)`;
    }
    
    // 上一个
    function prev() {
        currentIndex = (currentIndex - 1 + totalItems) % totalItems;
        updateCarousel();
    }
    
    // 下一个
    function next() {
        currentIndex = (currentIndex + 1) % totalItems;
        updateCarousel();
    }
    
    // 绑定按钮事件
    if (prevBtn) prevBtn.addEventListener('click', prev);
    if (nextBtn) nextBtn.addEventListener('click', next);
    
    // 指示器点击事件
    indicators.forEach((indicator, index) => {
        indicator.addEventListener('click', () => {
            currentIndex = index;
            updateCarousel();
        });
    });
    
    // 键盘导航
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft') prev();
        if (e.key === 'ArrowRight') next();
    });
    
    // 触摸滑动支持
    let touchStartX = 0;
    let touchEndX = 0;
    
    carousel.addEventListener('touchstart', (e) => {
        touchStartX = e.changedTouches[0].screenX;
    });
    
    carousel.addEventListener('touchend', (e) => {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
    });
    
    function handleSwipe() {
        const swipeThreshold = 50;
        const diff = touchStartX - touchEndX;
        
        if (Math.abs(diff) > swipeThreshold) {
            if (diff > 0) {
                next(); // 向左滑动，显示下一个
            } else {
                prev(); // 向右滑动，显示上一个
            }
        }
    }
});
