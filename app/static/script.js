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
function showImage(src) {
    const imgEl = document.getElementById('main-img');
    const videoEl = document.getElementById('main-video');
    const emptyEl = document.getElementById('main-img-empty');

    if (imgEl) {
      imgEl.src = src;
      imgEl.style.display = 'block';
    } else if (emptyEl) {
      emptyEl.style.display = 'block';
    }
    
    if (videoEl) {
      videoEl.style.display = 'none';
      videoEl.pause(); // Pausa o vídeo automaticamente ao sair dele
    }
  }

  function showVideo() {
    const imgEl = document.getElementById('main-img');
    const videoEl = document.getElementById('main-video');
    const emptyEl = document.getElementById('main-img-empty');

    if (imgEl) imgEl.style.display = 'none';
    if (emptyEl) emptyEl.style.display = 'none';
    
    if (videoEl) {
      videoEl.style.display = 'block';
      videoEl.play(); // Dá play automático ao clicar na miniatura (estilo Steam)
    }
  }
    function toggleEditMode() {
    const viewMode = document.getElementById('view-mode');
    const editMode = document.getElementById('edit-mode');
    
    if (viewMode.style.display === 'none') {
      viewMode.style.display = 'flex';
      editMode.style.display = 'none';
    } else {
      viewMode.style.display = 'none';
      editMode.style.display = 'flex';
    }
  }
  
function previewFoto(input) {
  const file = input.files && input.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = (e) => {
    const container = document.getElementById('avatar-preview');
    if (!container) return;

    // Se o avatar atual é a letra (usuário sem foto), troca por <img>.
    // Se já é <img>, só atualiza o src.
    let img = document.getElementById('avatar-img');
    if (!img) {
      container.innerHTML = '';
      img = document.createElement('img');
      img.id = 'avatar-img';
      img.style.cssText = 'width:100%;height:100%;border-radius:50%;object-fit:cover;';
      container.appendChild(img);
    }
    img.src = e.target.result;
  };
  reader.readAsDataURL(file);
}











































































































































































































































































































































































document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('form').forEach((form) => {
    if (form.dataset.noLock === 'true') return;

    form.addEventListener('submit', (event) => {
      if (form.dataset.locked === 'true') {
        event.preventDefault();
        return;
      }

      const button =
        form.querySelector('[data-submit-button]') ||
        event.submitter ||
        form.querySelector('button[type="submit"]') ||
        form.querySelector('button:not([type])');
      if (!button) return;

      form.dataset.locked = 'true';
      button.classList.add('is-locked');
      button.disabled = true;
      button.setAttribute('aria-disabled', 'true');
      button.setAttribute('aria-busy', 'true');
    });
  });
});
/* ================= CARRINHO ================= */

// Toda a lógica do carrinho: adicionar (via fetch), atualizar quantidade
// e remover item. Fica num DOMContentLoaded separado pra não colidir
// com o carrossel. Usa delegação de evento — funciona em qualquer
// página que tenha os botões com [data-add-to-cart] ou [data-item-id].
document.addEventListener('DOMContentLoaded', () => {

  // ── Utilitários ──

  function getCookie(name) {
    const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return v ? v.pop() : '';
  }

  async function postForm(url, data) {
    const body = new URLSearchParams(data);
    const resp = await fetch(url, {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body,
    });
    return resp.json();
  }

  function formatBRL(valor) {
    // Recebe "123.45" e devolve "R$ 123,45"
    const num = parseFloat(String(valor).replace(',', '.'));
    if (isNaN(num)) return 'R$ 0,00';
    return 'R$ ' + num.toFixed(2).replace('.', ',');
  }

  function atualizarBadgeCarrinho(quantidade) {
    const badge = document.querySelector('.cart-badge');
    if (!badge) return;
    if (quantidade > 0) {
      badge.textContent = quantidade;
    } else {
      badge.textContent = '0';
    }
  }

  // ── Adicionar ao carrinho ──
  // Delegação: funciona em home, produtos, detalhe. Basta o botão ter
  // [data-add-to-cart] e [data-produto-id]. Sem onclick inline.

  document.addEventListener('click', async (e) => {
    const btn = e.target.closest('[data-add-to-cart]');
    if (!btn) return;
    e.preventDefault();
    e.stopPropagation();   // impede que o clique no card abra o detalhe

    const produtoId = btn.dataset.produtoId;
    const quantidade = parseInt(btn.dataset.quantidade || '1', 10);
    if (!produtoId) return;

    const textoOriginal = btn.textContent;
    btn.disabled = true;
    btn.textContent = 'Adicionando...';

    try {
      const data = await postForm(`/carrinho/adicionar/${produtoId}/`, {
        quantidade: quantidade,
      });
      if (!data.ok) {
        alert(data.erro || 'Não foi possível adicionar ao carrinho.');
        btn.textContent = textoOriginal;
        btn.disabled = false;
        return;
      }
      atualizarBadgeCarrinho(data.quantidade_carrinho);
      btn.textContent = 'Adicionado!';
      setTimeout(() => {
        btn.textContent = textoOriginal;
        btn.disabled = false;
      }, 1200);
    } catch (err) {
      console.error('Erro ao adicionar:', err);
      alert('Erro de conexão. Tente novamente.');
      btn.textContent = textoOriginal;
      btn.disabled = false;
    }
  });

  // ── Página do carrinho: quantidade e remover ──
  // Só roda se a página atual for o carrinho (o wrapper .cart-items-column
  // só existe lá).

  const carrinhoPage = document.querySelector('.cart-items-column');
  if (!carrinhoPage) return;

  function atualizarResumo(subtotal, quantidadeCarrinho) {
    const elSub = document.getElementById('subtotal-carrinho');
    const elTotal = document.getElementById('total-carrinho');
    const elLabel = document.getElementById('resumo-label-itens');
    if (elSub) elSub.textContent = formatBRL(subtotal);
    if (elTotal) elTotal.textContent = formatBRL(subtotal);
    if (elLabel && quantidadeCarrinho !== undefined) {
      const palavra = quantidadeCarrinho === 1 ? 'item' : 'itens';
      elLabel.textContent = `Subtotal (${quantidadeCarrinho} ${palavra})`;
    }
    atualizarBadgeCarrinho(quantidadeCarrinho);
  }

  document.addEventListener('click', async (e) => {
    const btnQty = e.target.closest('.qty-btn');
    const btnRemover = e.target.closest('.remover-item');

        if (btnQty) {
      const row = btnQty.closest('.cart-item-row');
      const itemId = row.dataset.itemId;
      const qtyEl = row.querySelector('.qty-value');
      const subtotalEl = row.querySelector('.item-subtotal');
      const qtyControl = row.querySelector('.qty-control');
      const btnInc = row.querySelector('.qty-btn[data-action="increment"]');
      const btnDec = row.querySelector('.qty-btn[data-action="decrement"]');
      const estoque = qtyControl ? parseInt(qtyControl.dataset.estoque || '0', 10) : 0;

      let qtd = parseInt(qtyEl.textContent, 10);
      if (btnQty.dataset.action === 'increment') qtd += 1;
      else qtd = Math.max(1, qtd - 1);

      // Trava local: não bate no servidor se já sabemos que vai passar.
      if (btnQty.dataset.action === 'increment' && qtd > estoque) return;

      const data = await postForm(`/carrinho/item/${itemId}/quantidade/`, { quantidade: qtd });
      if (!data.ok) {
        alert(data.erro || 'Erro ao atualizar.');
        return;
      }

      qtyEl.textContent = data.quantidade;

      // Atualiza estado dos botões: + desabilita no limite, - desabilita em 1.
      if (btnInc) btnInc.disabled = data.quantidade >= estoque;
      if (btnDec) btnDec.disabled = data.quantidade <= 1;

      // Hint "Máximo disponível" aparece/some conforme o limite.
      let hintEl = row.querySelector('.qty-limit-hint');
      if (data.quantidade >= estoque) {
        if (!hintEl && qtyControl) {
          hintEl = document.createElement('span');
          hintEl.className = 'qty-limit-hint';
          hintEl.textContent = 'Máximo disponível';
          qtyControl.parentNode.insertBefore(hintEl, qtyControl.nextSibling);
        }
      } else if (hintEl) {
        hintEl.remove();
      }

      subtotalEl.textContent = formatBRL(data.subtotal_item);
      atualizarResumo(data.subtotal_carrinho, data.quantidade_carrinho);
    }

    if (btnRemover) {
      const row = btnRemover.closest('.cart-item-row');
      const itemId = row.dataset.itemId;
      const data = await postForm(`/carrinho/item/${itemId}/remover/`, {});
      if (!data.ok) {
        alert(data.erro || 'Erro ao remover.');
        return;
      }
      row.remove();
      atualizarResumo(data.subtotal_carrinho, data.quantidade_carrinho);
      if (data.carrinho_vazio) {
        window.location.reload();
      }
    }
  });

});