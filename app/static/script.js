document.addEventListener('DOMContentLoaded', () => {
  const slidesContainer = document.getElementById('carousel-slides');
  const slides = document.querySelectorAll('.slide');
  const dots = document.querySelectorAll('.dot');
  const btnPrev = document.getElementById('btn-prev');
  const btnNext = document.getElementById('btn-next');

  // Trava de segurança: se não houver carrossel na página, encerra o script aqui
  if (!slidesContainer) return;

  let currentSlide = 0;
  const totalSlides = slides.length;
  
  // 1. Criamos uma variável para controlar o timer do autoplay
  let autoPlayTimer;

  function updateCarousel() {
    slidesContainer.style.transform = `translateX(-${currentSlide * 100}%)`;
    
    dots.forEach((dot, index) => {
      if (index === currentSlide) {
        dot.classList.add('active');
      } else {
        dot.classList.remove('active');
      }
    });
  }

  function nextSlide() {
    currentSlide = (currentSlide + 1) % totalSlides;
    updateCarousel();
  }

  function prevSlide() {
    currentSlide = (currentSlide - 1 + totalSlides) % totalSlides;
    updateCarousel();
  }

  // 2. Criamos uma função que cancela o timer automático
  function stopAutoPlay() {
    clearInterval(autoPlayTimer);
  }

  // 3. Adicionamos a função stopAutoPlay antes de mudar o slide no clique
  if (btnNext) {
    btnNext.addEventListener('click', () => {
      stopAutoPlay(); // Para o automático
      nextSlide();    // Muda o slide manualmente
    });
  }

  if (btnPrev) {
    btnPrev.addEventListener('click', () => {
      stopAutoPlay();
      prevSlide();
    });
  }

  dots.forEach((dot, index) => {
    dot.addEventListener('click', () => {
      stopAutoPlay();
      currentSlide = index;
      updateCarousel();
    });
  });

  // 4. Iniciamos o timer guardando ele na nossa variável
  autoPlayTimer = setInterval(nextSlide, 5000);
});