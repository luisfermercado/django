(function () {
  'use strict';

  /* ---- Selector de audiencia del hero ---- */
  var heroes = {
    emp: { kicker: 'Para emprendimientos con tracción', title: 'Tu empresa, lista para el capital', body: 'Convertimos emprendimientos con tracción en empresas financiables: números defendibles, datos que respaldan cada supuesto y fundadores que saben contarlo.', cta: 'Hacer mi Capital Check AI', href: '#capital-check' },
    pyme: { kicker: 'Para pymes que necesitan crédito o fondos', title: 'Llega al banco con los números en orden', body: 'Ordenamos tus estados financieros, proyectamos tu flujo de caja y te conectamos con las líneas de crédito, fondos públicos y cooperación que sí te corresponden.', cta: 'Hacer mi Capital Check AI', href: '#capital-check' },
    inst: { kicker: 'Para gobiernos, cámaras y cooperación', title: 'Programas que se miden en capital movilizado', body: 'Diseñamos y operamos programas de alistamiento financiero con metas de financiación, tablero de seguimiento y reporte de resultados por empresa.', cta: 'Conocer Programs', href: '#programs' },
    inv: { kicker: 'Para inversionistas y entidades financieras', title: 'Empresas depuradas, con data room listo', body: 'Te presentamos empresas del suroccidente colombiano con modelo financiero, métricas verificables y fundadores preparados para la conversación.', cta: 'Unirme a la red de inversión', href: '#contacto' }
  };

  var audButtons = document.querySelectorAll('[data-aud]');
  function hero(name) { return document.querySelector('[data-hero="' + name + '"]'); }
  audButtons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var h = heroes[btn.dataset.aud];
      audButtons.forEach(function (b) { b.setAttribute('aria-pressed', b === btn ? 'true' : 'false'); });
      hero('kicker').textContent = h.kicker;
      hero('title').textContent = h.title;
      hero('body').textContent = h.body;
      hero('cta').textContent = h.cta;
      hero('cta').setAttribute('href', h.href);
    });
  });

  /* ---- Capital Check AI exprés ---- */
  var root = document.querySelector('[data-quiz]');
  if (!root) return;

  var questions = [
    { dim: 'num', label: 'Números', text: '¿Tienes estados financieros del último año?', options: [['Sí, completos y al día', 2], ['Parciales o desactualizados', 1], ['No los tengo', 0]] },
    { dim: 'num', label: 'Números', text: '¿Tienes proyecciones financieras a tres años con sus supuestos?', options: [['Sí, con supuestos explicados', 2], ['Un borrador', 1], ['No', 0]] },
    { dim: 'dat', label: 'Datos', text: '¿Mides los indicadores clave de tu negocio cada mes?', options: [['Sí, en un tablero', 2], ['A veces, en hojas sueltas', 1], ['No los mido', 0]] },
    { dim: 'nar', label: 'Narrativa', text: '¿Puedes explicar tu negocio y cuánto capital necesitas en dos minutos?', options: [['Sí, ya lo he presentado', 2], ['Más o menos', 1], ['Todavía no', 0]] },
    { dim: 'cap', label: 'Capital', text: '¿Qué tipo de capital buscas?', options: [['Crédito', 'cred'], ['Inversión', 'inv'], ['Fondos públicos o cooperación', 'fond'], ['Aún no lo sé', 'nose']] }
  ];
  var recs = {
    num: { svc: 'Capital Sprint', txt: 'Tu prioridad es ordenar los números: modelo financiero, proyecciones y valoración defendibles en 8 a 10 semanas.' },
    dat: { svc: 'Agente CFO', txt: 'Tu prioridad es medir: un tablero de indicadores con alertas y una revisión experta cada mes.' },
    nar: { svc: 'Pitch Lab', txt: 'Tu prioridad es contarlo: narrativa de inversión, oratoria y práctica con el Pitch Gym.' },
    all: { svc: 'Fundraising', txt: 'Tus tres barras están sólidas. Estás listo para salir a buscar capital y te acompañamos en el proceso.' }
  };
  var caps = {
    cred: 'Capital que te corresponde: crédito, con bancos y líneas de fomento.',
    inv: 'Capital que te corresponde: inversión, con ángeles y fondos.',
    fond: 'Capital que te corresponde: recursos no reembolsables, en convocatorias públicas y cooperación.',
    nose: 'El tipo de capital lo definimos contigo en el diagnóstico completo.'
  };

  var $ = function (sel) { return root.querySelector(sel); };
  var stepEl = $('[data-quiz-step]');
  var resultEl = $('[data-quiz-result]');
  var form = $('[data-quiz-form]');
  var sentEl = $('[data-quiz-sent]');
  var errorEl = $('[data-quiz-error]');
  var state = { step: 0, ans: [] };
  var lastResult = null;

  function level(s) { return s >= 4 ? 'Sólido' : (s >= 2 ? 'En progreso' : 'Por construir'); }

  function renderQuestion(focus) {
    var q = questions[state.step];
    stepEl.hidden = false;
    resultEl.hidden = true;
    root.querySelectorAll('.quiz__progress span').forEach(function (s, i) {
      s.className = i < state.step ? 'is-done' : (i === state.step ? 'is-current' : '');
    });
    $('[data-quiz-label]').textContent = 'Pregunta ' + (state.step + 1) + ' de 5 · ' + q.label;
    $('[data-quiz-question]').textContent = q.text;
    var opts = $('[data-quiz-options]');
    opts.innerHTML = '';
    q.options.forEach(function (o) {
      var b = document.createElement('button');
      b.type = 'button';
      b.textContent = o[0];
      b.addEventListener('click', function () {
        state.ans = state.ans.slice(0, state.step);
        state.ans.push(o[1]);
        state.step += 1;
        state.step < questions.length ? renderQuestion(true) : renderResult();
      });
      opts.appendChild(b);
    });
    $('[data-quiz-back]').hidden = state.step === 0;
    if (focus) $('[data-quiz-question]').focus();
  }

  function renderResult() {
    var a = state.ans;
    var scores = { num: a[0] + a[1], dat: a[2] * 2, nar: a[3] * 2 };
    stepEl.hidden = true;
    resultEl.hidden = false;
    Object.keys(scores).forEach(function (k) {
      root.querySelector('[data-bar="' + k + '"]').style.height = (40 + scores[k] * 50) + 'px';
      root.querySelector('[data-level="' + k + '"]').textContent = level(scores[k]);
    });
    var weakest = 'num';
    if (scores.dat < scores[weakest]) weakest = 'dat';
    if (scores.nar < scores[weakest]) weakest = 'nar';
    var rec = scores[weakest] >= 4 ? recs.all : recs[weakest];
    $('[data-rec="svc"]').textContent = rec.svc;
    $('[data-rec="txt"]').textContent = rec.txt;
    $('[data-rec="cap"]').textContent = caps[a[4]] || caps.nose;
    lastResult = { scores: scores, capital: a[4], recommendation: rec.svc, answers: a };
    $('[data-rec="svc"]').focus();
  }

  $('[data-quiz-back]').addEventListener('click', function () {
    state.step = Math.max(0, state.step - 1);
    renderQuestion(true);
  });
  $('[data-quiz-restart]').addEventListener('click', function () {
    state = { step: 0, ans: [] };
    form.hidden = false;
    sentEl.hidden = true;
    errorEl.hidden = true;
    renderQuestion(true);
  });

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    form.querySelector('[name="diagnosis"]').value = JSON.stringify(lastResult);
    errorEl.hidden = true;
    
    var submitBtn = form.querySelector('button[type="submit"]');
    var originalBtnText = submitBtn.textContent;
    submitBtn.textContent = 'Enviando...';
    submitBtn.disabled = true;

    fetch(form.action, { method: 'POST', body: new FormData(form), headers: { Accept: 'application/json' }, credentials: 'same-origin' })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function () { 
        form.hidden = true; 
        sentEl.hidden = false; 
      })
      .catch(function () { 
        errorEl.hidden = false;
        submitBtn.textContent = originalBtnText;
        submitBtn.disabled = false;
      });
  });

  renderQuestion(false);
})();
