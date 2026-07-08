var _pendingLoad = null;
var _state = { captureId: null, words: [] };

function setProcessing(processing) {
  var editBtn = document.getElementById('edit-ocr-btn');
  var redoBtn = document.getElementById('redo-ocr-btn');
  if (editBtn) editBtn.disabled = processing;
  if (redoBtn) redoBtn.disabled = processing;
}

document.getElementById('edit-ocr-btn')?.addEventListener('click', function() {
  if (!_state.captureId) return;
  openEditor();
});

document.getElementById('ocr-editor-save')?.addEventListener('click', function() {
  if (!_state.captureId) return;
  saveEditor();
});

document.getElementById('ocr-editor-cancel')?.addEventListener('click', closeEditor);

document.body.addEventListener('redo-ocr', function() {
  var overlay = document.getElementById('overlay');
  var status = document.getElementById('status');
  if (!_state.captureId) return;
  overlay.innerHTML = '';
  setProcessing(true);
  status.textContent = 'OCR processing...';
  if (_pendingLoad) { clearTimeout(_pendingLoad); }
  _pendingLoad = setTimeout(function() { loadOCR(_state.captureId, document.getElementById('screenshot'), overlay, status); }, 1500);
});

function initOverlay(captureId, ocrReady) {
  if (_pendingLoad) { clearTimeout(_pendingLoad); _pendingLoad = null; }
  _state.captureId = captureId;
  _state.words = [];
  var image = document.getElementById('screenshot');
  var overlay = document.getElementById('overlay');
  var status = document.getElementById('status');

  if (ocrReady) {
    loadOCR(captureId, image, overlay, status);
  } else {
    setProcessing(true);
    status.textContent = 'OCR processing...';
    _pendingLoad = setTimeout(function() { loadOCR(captureId, image, overlay, status); }, 1500);
  }
}

function loadOCR(captureId, image, overlay, status) {
  fetch('/captures/' + captureId + '/ocr')
    .then(function (resp) {
      if (!resp.ok) {
        if (resp.status === 404) {
          status.textContent = 'OCR processing... retrying';
          _pendingLoad = setTimeout(function() { loadOCR(captureId, image, overlay, status); }, 2000);
          return null;
        }
        throw new Error('HTTP ' + resp.status);
      }
      return resp.json();
    })
    .then(function (data) {
      if (!data) return;
      setProcessing(false);
      if (data.words && data.words.length > 0) {
        renderOverlay(data.words, image, overlay);
        status.textContent = 'OCR complete \u2014 ' + data.words.length + ' words';
      } else {
        status.textContent = 'OCR complete \u2014 no text found';
      }
    })
    .catch(function (err) {
      setProcessing(false);
      status.textContent = 'OCR failed';
      console.error(err);
    });
}

function renderOverlay(words, image, overlay) {
  if (!image.complete || image.naturalWidth === 0) {
    image.onload = function () { renderOverlay(words, image, overlay); };
    return;
  }

  overlay.innerHTML = '';
  var imgW = image.naturalWidth;
  var imgH = image.naturalHeight;

  for (var i = 0; i < words.length; i++) {
    var word = words[i];
    if (!word.bbox) continue;
    var bbox = word.bbox;
    var x1 = bbox[0][0], y1 = bbox[0][1];
    var x2 = bbox[1][0], y2 = bbox[1][1];
    var x3 = bbox[2][0], y3 = bbox[2][1];
    var x4 = bbox[3][0], y4 = bbox[3][1];

    var left   = (Math.min(x1, x4) / imgW) * 100;
    var top    = (Math.min(y1, y2) / imgH) * 100;
    var width  = ((Math.max(x2, x3) - Math.min(x1, x4)) / imgW) * 100;
    var height = ((Math.max(y3, y4) - Math.min(y1, y2)) / imgH) * 100;

    var span = document.createElement('span');
    span.textContent = word.text;
    span.style.left = left + '%';
    span.style.top = top + '%';
    span.style.width = width + '%';
    span.style.height = height + '%';
    span.style.fontSize = ((height / 100) * image.offsetHeight * 0.8) + 'px';
    span.style.lineHeight = '1';

    overlay.appendChild(span);
  }
}

function openEditor() {
  fetch('/captures/' + _state.captureId + '/ocr')
    .then(function (r) { return r.json(); })
    .then(function (data) {
      _state.words.length = 0;
      (data.words || []).forEach(function(w) { _state.words.push(w); });
      renderEditor(_state.words);
      document.getElementById('ocr-editor').style.display = 'block';
    });
}

function renderEditor(words) {
  var list = document.getElementById('ocr-editor-list');
  list.innerHTML = '';
  for (var i = 0; i < words.length; i++) {
    var w = words[i];
    var div = document.createElement('div');
    div.className = 'ocr-editor-word';

    var input = document.createElement('input');
    input.type = 'text';
    input.value = w.text;
    input.className = 'ocr-editor-input';
    input.dataset.index = i;

    var conf = document.createElement('span');
    conf.className = 'ocr-editor-conf';
    conf.textContent = Math.round((w.confidence || 0) * 100) + '%';

    div.appendChild(input);
    div.appendChild(conf);
    list.appendChild(div);
  }
}

function saveEditor() {
  var inputs = document.querySelectorAll('.ocr-editor-input');
  for (var i = 0; i < inputs.length; i++) {
    var idx = parseInt(inputs[i].dataset.index);
    if (_state.words[idx]) {
      _state.words[idx].text = inputs[i].value;
    }
  }

  fetch('/captures/' + _state.captureId + '/ocr', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ words: _state.words }),
  })
    .then(function (r) {
      if (r.ok) {
          closeEditor();
          var overlay = document.getElementById('overlay');
          overlay.innerHTML = '';
          renderOverlay(_state.words, document.getElementById('screenshot'), overlay);
          document.getElementById('status').textContent = 'OCR complete \u2014 ' + _state.words.length + ' words';
        }
    });
}

function closeEditor() {
  document.getElementById('ocr-editor').style.display = 'none';
}
