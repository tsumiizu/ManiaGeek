/* ════════════════════════════════════════════════════════════════
   MANIA GEEK — SCRIPT PRINCIPAL (CARROSSEL, FAQ, CARRINHO & CONTATO)
   ════════════════════════════════════════════════════════════════ */

let slideAtual = 0;
let carrosselTimer = null;
let totalSlides = 0;
let carrinhoContador = 0;

document.addEventListener('DOMContentLoaded', () => {
  inicializarCarrossel();
});

/* ── CARROSSEL AUTOMÁTICO ── */
function inicializarCarrossel() {
  const slidesContainer = document.getElementById('carousel-slides');
  const slides = document.querySelectorAll('.slide');
  const dots = document.querySelectorAll('.dot');
  const btnPrev = document.getElementById('btn-prev');
  const btnNext = document.getElementById('btn-next');
  const carouselElem = document.getElementById('hero-carousel');

  if (!slidesContainer || slides.length === 0) return;

  totalSlides = slides.length;

  if (btnPrev) btnPrev.addEventListener('click', () => mudarSlide(-1));
  if (btnNext) btnNext.addEventListener('click', () => mudarSlide(1));

  dots.forEach(dot => {
    dot.addEventListener('click', (e) => {
      const index = parseInt(e.target.getAttribute('data-slide'), 10);
      irParaSlide(index);
    });
  });

  // Pausa a rotação ao passar o mouse sobre o banner
  if (carouselElem) {
    carouselElem.addEventListener('mouseenter', pararAutoPlay);
    carouselElem.addEventListener('mouseleave', iniciarAutoPlay);
  }

  iniciarAutoPlay();
}

function atualizarCarrossel() {
  const slidesContainer = document.getElementById('carousel-slides');
  const dots = document.querySelectorAll('.dot');

  if (!slidesContainer) return;

  slidesContainer.style.transform = `translateX(-${slideAtual * 100}%)`;

  dots.forEach((dot, index) => {
    dot.classList.toggle('active', index === slideAtual);
  });
}

function mudarSlide(direcao) {
  slideAtual = (slideAtual + direcao + totalSlides) % totalSlides;
  atualizarCarrossel();
  reiniciarAutoPlay();
}

function irParaSlide(index) {
  slideAtual = index;
  atualizarCarrossel();
  reiniciarAutoPlay();
}

function iniciarAutoPlay() {
  pararAutoPlay();
  carrosselTimer = setInterval(() => {
    mudarSlide(1);
  }, 5500);
}

function pararAutoPlay() {
  if (carrosselTimer) {
    clearInterval(carrosselTimer);
    carrosselTimer = null;
  }
}

function reiniciarAutoPlay() {
  pararAutoPlay();
  iniciarAutoPlay();
}

/* ── FAQ (SANFONA) ── */
function toggleFaq(elemento) {
  elemento.classList.toggle('active');
}

/* ── CARRINHO & TOAST ── */
function adicionarAoCarrinho(nomeProduto, preco) {
  carrinhoContador++;
  const cartBadge = document.getElementById('cart-count');
  if (cartBadge) {
    cartBadge.textContent = carrinhoContador;
  }

  mostrarToast(`"${nomeProduto}" foi adicionado ao carrinho!`);
}

function abrirCarrinho() {
  if (carrinhoContador === 0) {
    mostrarToast('Seu carrinho está vazio.');
  } else {
    mostrarToast(`Seu carrinho possui ${carrinhoContador} item(ns).`);
  }
}

/* ── FORMULÁRIO DE CONTATO ── */
function enviarContato(event) {
  event.preventDefault();

  const nomeInput = document.getElementById('f-nome');
  const nome = nomeInput ? nomeInput.value : '';

  mostrarToast(`Obrigado, ${nome}! Sua mensagem foi enviada com sucesso.`);
  document.getElementById('contatoForm').reset();
}

/* ── TOAST ── */
function mostrarToast(mensagem) {
  const toast = document.getElementById('toast');
  if (!toast) return;

  toast.textContent = mensagem;
  toast.classList.add('show');

  setTimeout(() => {
    toast.classList.remove('show');
  }, 3500);
}
