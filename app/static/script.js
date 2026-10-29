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
/* ================= PRODUTO FORM: PREVIEWS ================= */
// Preview da capa do produto.
function previewImage(input) {
  const preview = document.getElementById('cover-preview');
  const hint = document.getElementById('cover-text-hint');
  if (!preview || !input.files || !input.files[0]) return;

  const reader = new FileReader();
  reader.onload = function (e) {
    preview.src = e.target.result;
    preview.classList.remove('preview-target-empty');
    if (hint) {
      hint.innerText = input.files[0].name;
      hint.style.color = 'var(--cyan)';
    }
  };
  reader.readAsDataURL(input.files[0]);
}
// Preview do vídeo demonstrativo.
function previewVideo(input) {
  const video = document.getElementById('video-preview');
  const placeholder = document.getElementById('video-placeholder');
  if (!video || !input.files || !input.files[0]) return;

  video.src = URL.createObjectURL(input.files[0]);
  video.classList.remove('hidden');
  if (placeholder) placeholder.classList.add('hidden');
}
// Preview de cada imagem extra.
function previewExtra(input, idx) {
  const preview = document.getElementById('extra-preview-' + idx);
  const placeholder = document.getElementById('extra-placeholder-' + idx);
  if (!preview || !input.files || !input.files[0]) return;

  const reader = new FileReader();
  reader.onload = function (e) {
    preview.src = e.target.result;
    preview.classList.remove('hidden');
    if (placeholder) placeholder.classList.add('hidden');
  };
  reader.readAsDataURL(input.files[0]);
}
/* ================= ENDEREÇO FORM: ViaCEP + VALIDAÇÃO DO BOTÃO ================= */

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('form-endereco');
  if (!form) return;
  const inputCep = document.getElementById('id_cep');
  const inputEndereco = document.getElementById('id_endereco');
  const inputBairro = document.getElementById('id_bairro');
  const inputCidade = document.getElementById('id_cidade');
  const inputEstado = document.getElementById('id_estado');
  const statusEl = document.getElementById('cep-status');
  const btnSalvar = form.querySelector('[data-submit-button]');
  if (!inputCep || !btnSalvar) return;
  // ── Campos que precisam estar preenchidos pro botão liberar ──
  const camposObrigatorios = [
    'id_cep',
    'id_endereco',
    'id_numero',
    'id_bairro',
    'id_cidade',
    'id_estado',
  ];
  const textoOriginalBotao = btnSalvar.textContent;
  // ── Utilitário: só dígitos ──
  function apenasDigitos(str) {
    return (str || '').replace(/\D/g, '');
  }
  // ── Utilitário: 00000000 -> 00000-000 ──
  function formatarCep(valor) {
    const d = apenasDigitos(valor).slice(0, 8);
    if (d.length <= 5) return d;
    return d.slice(0, 5) + '-' + d.slice(5);
  }
  // ── Utilitário: mensagem abaixo do CEP ──
  function setStatus(msg, cor) {
    if (!statusEl) return;
    statusEl.textContent = msg;
    statusEl.style.color = cor || 'var(--text-muted)';
  }
  // ── Limpa os campos preenchidos pelo ViaCEP ──
  function limparEndereco() {
    inputEndereco.value = '';
    inputBairro.value = '';
    inputCidade.value = '';
    inputEstado.value = '';
  }
  // ── Validação do botão ──
  function todosPreenchidos() {
    for (const id of camposObrigatorios) {
      const el = document.getElementById(id);
      if (!el) continue;
      if (!el.value || !el.value.trim()) return false;
    }
    return true;
  }
  function atualizarEstadoBotao() {
    if (todosPreenchidos()) {
      btnSalvar.disabled = false;
      btnSalvar.removeAttribute('aria-disabled');
      btnSalvar.textContent = textoOriginalBotao;
    } else {
      btnSalvar.disabled = true;
      btnSalvar.setAttribute('aria-disabled', 'true');
      btnSalvar.textContent = 'Preencha os campos';
    }
  }
  // ── Busca CEP no ViaCEP ──
  async function buscarCep() {
    const cepLimpo = apenasDigitos(inputCep.value);
    if (cepLimpo.length === 0) {
      limparEndereco();
      setStatus('', '');
      atualizarEstadoBotao();
      return;
    }
    if (cepLimpo.length !== 8) {
      setStatus('CEP incompleto.', 'var(--yellow)');
      return;
    }
    setStatus('Buscando CEP...', 'var(--cyan)');
    try {
      const resp = await fetch(`https://viacep.com.br/ws/${cepLimpo}/json/`);
      if (!resp.ok) throw new Error('Falha na rede');
      const dados = await resp.json();
      if (dados.erro) {
        limparEndereco();
        setStatus('CEP não encontrado.', '#e63946');
        atualizarEstadoBotao();
        return;
      }
      inputEndereco.value = dados.logradouro || '';
      inputBairro.value = dados.bairro || '';
      inputCidade.value = dados.localidade || '';
      inputEstado.value = dados.uf || '';
      setStatus('Endereço preenchido automaticamente.', 'var(--cyan)');
      atualizarEstadoBotao();
    } catch (err) {
      console.error('Erro ao consultar ViaCEP:', err);
      setStatus('Erro ao consultar o CEP. Tente novamente.', '#e63946');
      atualizarEstadoBotao();
    }
  }
  // ── Formata o CEP enquanto o usuário digita ──
  inputCep.addEventListener('input', (e) => {
    e.target.value = formatarCep(e.target.value);
  });
  // ── Dispara a busca ao sair do campo ──
  inputCep.addEventListener('blur', buscarCep);
  // ── Dispara a busca com Enter ──
  inputCep.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      buscarCep();
    }
  });
  // ── Escuta mudanças em todos os inputs do form pra reavaliar o botão ──
  form.querySelectorAll('input').forEach((el) => {
    el.addEventListener('input', atualizarEstadoBotao);
    el.addEventListener('change', atualizarEstadoBotao);
  });
  // ── Estado inicial: cobre edição (campos já preenchidos) ──
  atualizarEstadoBotao();
  // ── Se já veio com CEP (edição), busca o endereço ──
  if (apenasDigitos(inputCep.value).length === 8) {
    buscarCep();
  }
});





/* ════════════════════════════════════════════════════════════════
   Bolinha vermelha de "pedido entregue" (perfil + navbar)
   Cole no FIM do script.js.
   - Some quando o usuário clica em "Pedidos concluídos" pela 1ª vez.
   - Fica salvo no navegador (localStorage), então não volta ao recarregar.
   - Um pedido entregue novo (outro id) acende a bolinha de novo.
   ════════════════════════════════════════════════════════════════ */
(function () {
  var marcadores = document.querySelectorAll('[data-entregue]');
  if (!marcadores.length) return;

  var chave = 'mg_entregues_vistos_' + (marcadores[0].dataset.uid || 'anon');

  function ler() {
    try { return JSON.parse(localStorage.getItem(chave)) || []; } catch (e) { return []; }
  }
  function gravar(lista) {
    try { localStorage.setItem(chave, JSON.stringify(lista)); } catch (e) {}
  }

  // Já visto antes: remove a bolinha (e a etiqueta "Novo") logo ao carregar
  var vistos = ler();
  marcadores.forEach(function (el) {
    if (vistos.indexOf(el.dataset.entregue) !== -1) el.remove();
  });

  // Terminou de conferir: agora as bolinhas que sobraram podem aparecer
  // (o CSS as mantém invisíveis até aqui, para não piscar ao recarregar)
  document.documentElement.classList.add('bolinha-pronta');

  // Primeiro clique na aba "Pedidos concluídos": grava como visto e some com as bolinhas
  function marcarVistos() {
    var atuais = ler();
    document.querySelectorAll('[data-entregue]').forEach(function (el) {
      if (atuais.indexOf(el.dataset.entregue) === -1) atuais.push(el.dataset.entregue);
    });
    gravar(atuais);
    document.querySelectorAll('.conta-dot').forEach(function (el) { el.remove(); });
  }

  var radio = document.getElementById('r-concluidos');
  if (radio) radio.addEventListener('change', function () { if (radio.checked) marcarVistos(); });
})();







(function () {
  var link = document.querySelector('a[data-eventos-link]');
  if (!link) return;
 
  var CHAVE = 'mg_eventos_visto';
  var tokenAtual = '';
 
  function lerVisto() {
    try { return localStorage.getItem(CHAVE) || ''; } catch (e) { return ''; }
  }
  function gravarVisto(token) {
    try { localStorage.setItem(CHAVE, token); } catch (e) {}
  }
  function mostrarBolinha() {
    if (link.querySelector('.nav-evento-dot')) return;
    var dot = document.createElement('span');
    dot.className = 'nav-evento-dot';
    dot.setAttribute('aria-label', 'Novidade nos eventos');
    link.appendChild(dot);
  }
  function esconderBolinha() {
    var dot = link.querySelector('.nav-evento-dot');
    if (dot) dot.remove();
  }
 
  // Na própria página de eventos: abrir a página já conta como "visto".
  var pagina = document.querySelector('.ev-page[data-token]');
  if (pagina) {
    gravarVisto(pagina.dataset.token || '');
    return;
  }
 
  // Nas outras páginas: pergunta ao servidor se algo mudou desde a última visita.
  fetch(link.dataset.tokenUrl, { credentials: 'same-origin', cache: 'no-store' })
    .then(function (r) { return r.json(); })
    .then(function (dados) {
      tokenAtual = dados.token || '';
      if (tokenAtual && tokenAtual !== lerVisto()) mostrarBolinha();
    })
    .catch(function () {});
 
  // Clicou em "Eventos": some na hora e grava como visto.
  link.addEventListener('click', function () {
    if (tokenAtual) gravarVisto(tokenAtual);
    esconderBolinha();
  });
})();

























































































































































































































































































































































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
/* ================= CARRINHO ================= */
(function () {
  function getCookie(name) {
    var v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return v ? v.pop() : '';
  }

  function postForm(url, data) {
    var body = new URLSearchParams(data);
    return fetch(url, {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: body
    }).then(function (r) { return r.json(); });
  }

  function formatBRL(valor) {
    var num = parseFloat(String(valor).replace(',', '.'));
    if (isNaN(num)) return 'R$ 0,00';
    return 'R$ ' + num.toFixed(2).replace('.', ',');
  }

  function atualizarBadge(quantidade) {
    var badge = document.querySelector('.cart-badge');
    if (!badge) return;
    badge.textContent = quantidade > 0 ? quantidade : '0';
  }

  function showToast(mensagem, corFundo) {
    corFundo = corFundo || 'var(--cyan)';
    var toastEl = document.getElementById('toast');
    if (!toastEl) {
      console.warn('Elemento #toast não encontrado no DOM');
      return;
    }
    toastEl.textContent = mensagem;
    toastEl.style.backgroundColor = corFundo;
    toastEl.style.color = corFundo === 'var(--cyan)' ? 'var(--text-on-yellow)' : '#fff';
    toastEl.classList.add('show');
    setTimeout(function () { toastEl.classList.remove('show'); }, 3000);
  }

  // Adicionar ao carrinho — listener na FASE DE CAPTURA do document.
  // Isso roda antes de qualquer onclick inline do card. Sempre.
  document.addEventListener('click', function (e) {
    var btn = e.target.closest ? e.target.closest('[data-add-to-cart]') : null;
    if (!btn) return;

    // Mata o evento aqui. Não chega no onclick do .product-card.
    e.preventDefault();
    e.stopPropagation();
    e.stopImmediatePropagation();

    if (btn.dataset.adding === '1') return;
    if (btn.disabled) return;

    var produtoId = btn.dataset.produtoId;
    var quantidade = parseInt(btn.dataset.quantidade || '1', 10);
    if (!produtoId) return;

    btn.dataset.adding = '1';
    var textoOriginal = btn.textContent;
    btn.disabled = true;
    btn.textContent = 'Adicionando...';

    postForm('/carrinho/adicionar/' + produtoId + '/', { quantidade: quantidade })
      .then(function (data) {
        if (!data.ok) {
          showToast(data.erro || 'Não foi possível adicionar.', '#e63946');
          btn.textContent = textoOriginal;
          btn.disabled = false;
          btn.dataset.adding = '';
          return;
        }
        if (typeof data.quantidade_carrinho === 'number') {
          atualizarBadge(data.quantidade_carrinho);
        }
        showToast('Produto adicionado ao carrinho!');
        setTimeout(function () {
          btn.textContent = textoOriginal;
          btn.disabled = false;
          btn.dataset.adding = '';
        }, 600);
      })
      .catch(function (err) {
        console.error('Erro ao adicionar:', err);
        showToast('Erro de conexão. Tente novamente.', '#e63946');
        btn.textContent = textoOriginal;
        btn.disabled = false;
        btn.dataset.adding = '';
      });
  }, true);

  // ── Página do carrinho: quantidade e remover ──
  document.addEventListener('click', function (e) {
    var btnQty = e.target.closest ? e.target.closest('.qty-btn') : null;
    var btnRemover = e.target.closest ? e.target.closest('.remover-item') : null;

    if (btnQty) {
      var row = btnQty.closest('.cart-item-row');
      var itemId = row.dataset.itemId;
      var qtyEl = row.querySelector('.qty-value');
      var subtotalEl = row.querySelector('.item-subtotal');
      var qtyControl = row.querySelector('.qty-control');
      var btnInc = row.querySelector('.qty-btn[data-action="increment"]');
      var btnDec = row.querySelector('.qty-btn[data-action="decrement"]');
      var estoque = qtyControl ? parseInt(qtyControl.dataset.estoque || '0', 10) : 0;

      var qtd = parseInt(qtyEl.textContent, 10);
      if (btnQty.dataset.action === 'increment') qtd += 1;
      else qtd = Math.max(1, qtd - 1);
      if (btnQty.dataset.action === 'increment' && qtd > estoque) return;

      postForm('/carrinho/item/' + itemId + '/quantidade/', { quantidade: qtd })
        .then(function (data) {
          if (!data.ok) { alert(data.erro || 'Erro ao atualizar.'); return; }
          qtyEl.textContent = data.quantidade;
          if (btnInc) btnInc.disabled = data.quantidade >= estoque;
          if (btnDec) btnDec.disabled = data.quantidade <= 1;
          subtotalEl.textContent = formatBRL(data.subtotal_item);

          var elSub = document.getElementById('subtotal-carrinho');
          var elTotal = document.getElementById('total-carrinho');
          var elLabel = document.getElementById('resumo-label-itens');
          if (elSub) elSub.textContent = formatBRL(data.subtotal_carrinho);
          if (elTotal) elTotal.textContent = formatBRL(data.subtotal_carrinho);
          if (elLabel && data.quantidade_carrinho !== undefined) {
            elLabel.textContent = 'Subtotal (' + data.quantidade_carrinho + (data.quantidade_carrinho === 1 ? ' item' : ' itens') + ')';
          }
          atualizarBadge(data.quantidade_carrinho);
        });
    }

    if (btnRemover) {
      var rowR = btnRemover.closest('.cart-item-row');
      var itemIdR = rowR.dataset.itemId;
      postForm('/carrinho/item/' + itemIdR + '/remover/', {})
        .then(function (data) {
          if (!data.ok) { alert(data.erro || 'Erro ao remover.'); return; }
          rowR.remove();
          var elSub = document.getElementById('subtotal-carrinho');
          var elTotal = document.getElementById('total-carrinho');
          if (elSub) elSub.textContent = formatBRL(data.subtotal_carrinho);
          if (elTotal) elTotal.textContent = formatBRL(data.subtotal_carrinho);
          atualizarBadge(data.quantidade_carrinho);
          if (data.carrinho_vazio) window.location.reload();
        });
    }
  });
})();

/* ================= DASHBOARD: EDITOR DE CARGOS ================= */

document.addEventListener('DOMContentLoaded', () => {
  function getCookie(name) {
    const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return v ? v.pop() : '';
  }
  document.querySelectorAll('.cargo-editor').forEach(editor => {
    const url = editor.dataset.url;
    // Coleta os IDs de grupos atualmente aplicados lendo os
    // selects "editáveis" (um por grupo atual).
    function gruposAtuais() {
      return Array.from(
        editor.querySelectorAll('.cargo-select-editavel')
      ).map(s => s.value).filter(v => v !== '');
    }
    async function salvar(novosIds) {
      // Desabilita tudo enquanto salva
      editor.querySelectorAll('select').forEach(s => s.disabled = true);
      try {
        const body = new URLSearchParams();
        novosIds.forEach(id => body.append('grupos_ids', id));
        const resp = await fetch(url, {
          method: 'POST',
          headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body,
        });
        const data = await resp.json();
        if (!data.ok) {
          alert(data.erro || 'Erro ao atualizar.');
          // Recarrega a página pra voltar ao estado real. Menos
          // elegante que reverter no DOM, mas garante consistência
          // sem rastrear estado.
          window.location.reload();
          return;
        }
        // Sucesso: recarrega pra reconstruir os pills com o novo
        // estado. Simples e sempre correto.
        window.location.reload();
      } catch (err) {
        console.error('Erro ao salvar cargos:', err);
        alert('Erro de conexão. Tente novamente.');
        window.location.reload();
      }
    }
    // Selects de grupos existentes: trocar = remove o antigo + adiciona o novo
    editor.querySelectorAll('.cargo-select-editavel').forEach(select => {
      select.addEventListener('change', () => {
        const grupoAntigo = select.closest('.cargo-chip').dataset.grupoAtual;
        const novoGrupo = select.value;
        const atuais = gruposAtuais();
        // Remove o antigo
        const semAntigo = atuais.filter(id => id !== grupoAntigo);
        // Adiciona o novo, se veio um
        const final = novoGrupo ? [...semAntigo, novoGrupo] : semAntigo;
        // Remove duplicatas (por segurança)
        const unicos = [...new Set(final)];
        salvar(unicos);
      });
    });
    // Select "+ Adicionar": adiciona ao conjunto atual
    const addSelect = editor.querySelector('.cargo-select-add');
    if (addSelect) {
      addSelect.addEventListener('change', () => {
        const novoGrupo = addSelect.value;
        if (!novoGrupo) return;

        const atuais = gruposAtuais();
        const final = [...atuais, novoGrupo];
        const unicos = [...new Set(final)];
        salvar(unicos);
      });
    }
  });
});
/* ================= CHAT DO PEDIDO (polling incremental) ================= */

document.addEventListener('DOMContentLoaded', () => {
  const chatEl = document.getElementById('chat');
  if (!chatEl) return;

  const INTERVALO_POLLING_MS = 3000;
  const pedidoId = chatEl.dataset.pedidoId;
  const meuUserId = parseInt(chatEl.dataset.userId, 10);
  const encerrado = chatEl.dataset.chatEncerrado === 'true';

  const messagesEl = document.getElementById('chat-messages');
  if (!messagesEl) return;

  // Elementos do form só existem no modo ativo.
  const formEl = document.getElementById('chat-form');
  const inputEl = document.getElementById('chat-input');
  const sendBtn = document.getElementById('chat-send');

  let ultimoIdVisto = 0;
  let timerPolling = null;
  let enviando = false;

  function getCookie(name) {
    const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return v ? v.pop() : '';
  }

  function escaparHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  function formatarHora(isoString) {
    try {
      const d = new Date(isoString);
      const hh = String(d.getHours()).padStart(2, '0');
      const mm = String(d.getMinutes()).padStart(2, '0');
      return `${hh}:${mm}`;
    } catch {
      return '';
    }
  }

  function scrollParaFim() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function renderMensagem(msg) {
    const mine = (parseInt(msg.autor_id, 10) === meuUserId);

    const wrap = document.createElement('div');
    wrap.className = 'chat-msg ' + (mine ? 'chat-msg-mine' : 'chat-msg-theirs');

    const avatar = document.createElement('div');
    avatar.className = 'chat-msg-avatar';

    if (msg.autor_foto) {
      const img = document.createElement('img');
      img.src = msg.autor_foto;
      img.alt = msg.autor_nome;
      img.loading = 'lazy';
      avatar.appendChild(img);
    } else {
      const letra = (msg.autor_nome || '?').trim().charAt(0).toUpperCase();
      avatar.textContent = letra;
    }

    const corpo = document.createElement('div');
    corpo.className = 'chat-msg-body';

    const head = document.createElement('div');
    head.className = 'chat-msg-head';
    head.innerHTML = `
      <span class="chat-msg-name">${escaparHtml(msg.autor_nome)}</span>
      <span class="chat-msg-time">${formatarHora(msg.criado_em)}</span>
    `;

    const bubble = document.createElement('div');
    bubble.className = 'chat-msg-bubble';
    bubble.textContent = msg.conteudo;

    corpo.appendChild(head);
    corpo.appendChild(bubble);
    wrap.appendChild(avatar);
    wrap.appendChild(corpo);
    messagesEl.appendChild(wrap);
  }

  function limparPlaceholders() {
    const loading = messagesEl.querySelector('.chat-loading');
    const empty = messagesEl.querySelector('.chat-empty');
    if (loading) loading.remove();
    if (empty) empty.remove();
  }

  async function buscarMensagens() {
    const url = ultimoIdVisto > 0
      ? `/pedido/${pedidoId}/chat/mensagens/?desde_id=${ultimoIdVisto}`
      : `/pedido/${pedidoId}/chat/mensagens/`;

    try {
      const resp = await fetch(url, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
      });
      if (!resp.ok) return;
      const data = await resp.json();
      if (!data.ok) return;

      if (data.mensagens.length === 0 && ultimoIdVisto === 0) {
        limparPlaceholders();
        const emptyEl = document.createElement('div');
        emptyEl.className = 'chat-empty';
        emptyEl.textContent = 'Nenhuma mensagem nesta conversa.';
        messagesEl.appendChild(emptyEl);
        return;
      }

      if (data.mensagens.length === 0) return;

      limparPlaceholders();
      const estavaNoFim =
        messagesEl.scrollHeight - messagesEl.scrollTop - messagesEl.clientHeight < 40;

      data.mensagens.forEach((m) => {
        renderMensagem(m);
        const idNum = parseInt(m.id, 10);
        if (idNum > ultimoIdVisto) ultimoIdVisto = idNum;
      });

      if (estavaNoFim || ultimoIdVisto === 0) {
        scrollParaFim();
      }
    } catch (err) {
      console.error('Erro ao buscar mensagens:', err);
    }
  }

  async function enviarMensagem(e) {
    e.preventDefault();
    if (enviando) return;
    if (!inputEl || !sendBtn) return;

    const conteudo = inputEl.value.trim();
    if (!conteudo) return;

    enviando = true;
    sendBtn.disabled = true;

    try {
      const body = new URLSearchParams({ conteudo });
      const resp = await fetch(`/pedido/${pedidoId}/chat/enviar/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
          'X-Requested-With': 'XMLHttpRequest',
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body,
      });
      const data = await resp.json();
      if (!data.ok) {
        alert(data.erro || 'Não foi possível enviar a mensagem.');
        return;
      }

      limparPlaceholders();
      renderMensagem(data.mensagem);
      const idNum = parseInt(data.mensagem.id, 10);
      if (idNum > ultimoIdVisto) ultimoIdVisto = idNum;

      inputEl.value = '';
      inputEl.focus();
      scrollParaFim();
    } catch (err) {
      console.error('Erro ao enviar:', err);
      alert('Erro de conexão. Tente novamente.');
    } finally {
      enviando = false;
      sendBtn.disabled = false;
    }
  }

  function iniciarPolling() {
    if (timerPolling) return;
    timerPolling = setInterval(buscarMensagens, INTERVALO_POLLING_MS);
  }
  function pararPolling() {
    if (timerPolling) {
      clearInterval(timerPolling);
      timerPolling = null;
    }
  }

  // Listeners do form: só no modo ativo.
  if (!encerrado && formEl && inputEl && sendBtn) {
    inputEl.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        formEl.requestSubmit();
      }
    });
    formEl.addEventListener('submit', enviarMensagem);

    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        pararPolling();
      } else {
        buscarMensagens();
        iniciarPolling();
      }
    });
  }

  // ── Inicialização ──
  buscarMensagens().then(() => {
    scrollParaFim();
    if (!encerrado) {
      iniciarPolling();
    }
  });
});

/* ================= CHECKOUT: RESUMO REATIVO (TIPO DE ENTREGA + ENDEREÇO) ================= */

document.addEventListener('DOMContentLoaded', () => {
  const checkoutForm = document.getElementById('form-checkout');
  if (!checkoutForm) return;

  const radioEnvio = document.getElementById('entrega-envio');
  const radioCombinar = document.getElementById('entrega-combinar');
  if (!radioEnvio || !radioCombinar) return;

  const metaEl = document.getElementById('resumo-meta');
  const infoEl = document.getElementById('resumo-frete-info');
  const valorEl = document.getElementById('resumo-frete-valor');
  const totalEl = document.getElementById('resumo-total');
  if (!metaEl || !infoEl || !valorEl || !totalEl) return;

  // Subtotal nunca muda (vem do template)
  const subtotal = parseFloat(metaEl.dataset.subtotal) || 0;

  // Estado atual do frete (muda conforme endereço escolhido)
  let freteAtual = {
    valor: parseFloat(metaEl.dataset.frete) || 0,
    prazo: metaEl.dataset.prazo || '',
    transportadora: metaEl.dataset.transportadora || '',
  };

  // Cache simples por estado, pra não bater no backend toda vez
  const cacheFrete = {};

  function formatarMoedaBRL(valor) {
    return 'R$ ' + valor.toFixed(2).replace('.', ',');
  }

  function getEnderecoSelecionado() {
    return checkoutForm.querySelector('input[name="endereco_id"]:checked');
  }

  function renderResumo() {
    if (radioCombinar.checked) {
      infoEl.textContent = 'A combinar com o vendedor';
      valorEl.textContent = 'R$ 0,00';
      totalEl.textContent = formatarMoedaBRL(subtotal);
      return;
    }
    infoEl.textContent = `${freteAtual.transportadora} · ~${freteAtual.prazo} dias úteis`;
    valorEl.textContent = formatarMoedaBRL(freteAtual.valor);
    totalEl.textContent = formatarMoedaBRL(subtotal + freteAtual.valor);
  }

  async function buscarFretePara(estado) {
    if (!estado) return null;
    if (cacheFrete[estado]) return cacheFrete[estado];

    try {
      const resp = await fetch(`/api/frete/?estado=${encodeURIComponent(estado)}`);
      if (!resp.ok) return null;
      const data = await resp.json();
      if (!data.ok) return null;
      cacheFrete[estado] = {
        valor: parseFloat(data.valor) || 0,
        prazo: data.prazo,
        transportadora: data.transportadora,
      };
      return cacheFrete[estado];
    } catch (err) {
      console.error('Erro ao buscar frete:', err);
      return null;
    }
  }

  async function atualizarFretePeloEndereco() {
    // Se está em modo combinar, não busca frete
    if (radioCombinar.checked) {
      renderResumo();
      return;
    }

    const radio = getEnderecoSelecionado();
    if (!radio) return;

    const estado = radio.dataset.estado || '';
    if (!estado) {
      // Sem estado no endereço: mantém o que já estava
      renderResumo();
      return;
    }

    // Feedback visual enquanto busca
    infoEl.textContent = 'Calculando frete…';

    const novoFrete = await buscarFretePara(estado);
    if (novoFrete) {
      freteAtual = novoFrete;
    }
    renderResumo();
  }

  // Escuta mudança de tipo de entrega
  radioEnvio.addEventListener('change', () => {
    atualizarFretePeloEndereco();
  });
  radioCombinar.addEventListener('change', () => {
    renderResumo();
  });

  // Escuta mudança de endereço
  checkoutForm.querySelectorAll('input[name="endereco_id"]').forEach((radio) => {
    radio.addEventListener('change', atualizarFretePeloEndereco);
  });

  // Estado inicial
  renderResumo();
});