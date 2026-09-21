const PHASES = {
  latenza: {
    label: "Latenza",
    copy: "La coltura è ancora rada. La pompa resta ferma.",
  },
  crescita: {
    label: "Crescita",
    copy: "La densità sta salendo. La raccolta non è ancora partita.",
  },
  picco: {
    label: "Picco",
    copy: "Densità alta. La pompa è ancora ferma.",
  },
  raccolta: {
    label: "Raccolta",
    copy: "La pompa spinge la coltura nel filtro da 5 µm.",
  },
  recupero: {
    label: "Recupero",
    copy: "Dopo la raccolta si aspetta che la densità torni a salire.",
  },
};

const REASONS = {
  "below-threshold": "Sotto la soglia di raccolta.",
  "above-threshold": "Soglia di raccolta superata. La pompa è partita.",
  "above-off-threshold": "Filtraggio in corso, in attesa che la coltura si schiarisca.",
  "below-off-threshold": "Coltura sotto la soglia di riposo. Pompa ferma.",
  "min-on": "Tempo minimo di filtraggio, per non far battere il relè.",
  "min-off": "Pausa minima prima di una nuova accensione.",
  "manual-on": "Accensione manuale. L'automatico è sospeso.",
  "manual-off": "Spegnimento manuale. L'automatico è sospeso.",
  "sensor-fault": "Sensore non leggibile. In automatico la pompa resta spenta.",
};

const one = new Intl.NumberFormat("it-IT", {
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
});
const whole = new Intl.NumberFormat("it-IT", { maximumFractionDigits: 0 });

const panel = document.querySelector(".panel");
const faultEl = document.getElementById("fault");
const liveEl = document.getElementById("live");
let lastSpoken = "";
let misses = 0;
let busy = false;

function formatDuration(seconds) {
  const s = Math.max(0, Math.round(seconds));
  const m = Math.floor(s / 60);
  const rem = s % 60;
  if (m <= 0) return rem + " s";
  return m + " min " + String(rem).padStart(2, "0") + " s";
}

function formatRate(gramsPerHour) {
  if (gramsPerHour < 1) {
    return { value: whole.format(gramsPerHour * 1000), unit: "mg/h" };
  }
  return { value: one.format(gramsPerHour), unit: "g/h" };
}

function formatToday(grams) {
  if (grams < 1) return one.format(grams * 1000) + " mg oggi";
  return one.format(grams) + " g oggi";
}

function renderClock() {
  document.getElementById("clock").textContent = new Intl.DateTimeFormat("it-IT", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  }).format(new Date());
}

function setPressed(mode) {
  document.querySelectorAll(".actions button").forEach((button) => {
    button.setAttribute("aria-pressed", button.dataset.mode === mode ? "true" : "false");
  });
}

function showFault(message) {
  if (!message) {
    faultEl.hidden = true;
    faultEl.textContent = "";
    return;
  }
  faultEl.hidden = false;
  faultEl.textContent = message;
}

function drawHistory(values, threshold) {
  const canvas = document.getElementById("history");
  const dpr = window.devicePixelRatio || 1;
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;
  if (width < 2 || height < 2) return;
  canvas.width = Math.round(width * dpr);
  canvas.height = Math.round(height * dpr);
  const ctx = canvas.getContext("2d");
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, width, height);
  if (!values || values.length < 2) return;

  const styles = getComputedStyle(document.body);
  const accent = styles.getPropertyValue("--accent").trim() || "#8fb56f";
  const line = styles.getPropertyValue("--line").trim() || "#31443a";
  const max = Math.max(threshold || 0, ...values, 1);
  const yOf = (value) => height - (value / max) * (height - 4) - 2;

  if (threshold) {
    const y = yOf(threshold);
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(width, y);
    ctx.strokeStyle = line;
    ctx.lineWidth = 1;
    ctx.stroke();
  }

  ctx.beginPath();
  values.forEach((value, index) => {
    const x = (index / (values.length - 1)) * (width - 1);
    const y = yOf(value);
    if (index === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.strokeStyle = accent;
  ctx.lineWidth = 2;
  ctx.stroke();
}

function render(snap) {
  document.querySelectorAll(".actions button").forEach((button) => {
    button.disabled = !snap.ready;
  });
  if (snap.pump_mode) setPressed(snap.pump_mode);
  if (!snap.ready) return;

  document.body.classList.remove("is-booting");
  panel.setAttribute("aria-busy", "false");

  const phase = PHASES[snap.phase] || { label: snap.phase, copy: "" };
  document.getElementById("phase-now").textContent = phase.label;
  document.getElementById("phase-copy").textContent = phase.copy;
  document.querySelectorAll(".cycle li").forEach((item) => {
    if (item.dataset.phase === snap.phase) item.setAttribute("aria-current", "step");
    else item.removeAttribute("aria-current");
  });

  const turb = document.getElementById("turbidity-block");
  turb.classList.toggle("is-stale", !snap.sensor_ok && snap.turbidity_ntu != null);
  document.getElementById("ntu").textContent =
    snap.turbidity_ntu == null ? "assente" : one.format(snap.turbidity_ntu);

  const on = snap.thresholds ? snap.thresholds.on : 280;
  const off = snap.thresholds ? snap.thresholds.off : 90;
  let meta = "Raccolta a " + whole.format(on) + " NTU, riposo a " + whole.format(off) + " NTU";
  if (snap.turbidity_v != null) {
    meta = one.format(snap.turbidity_v) + " V sulla sonda. " + meta;
  }
  document.getElementById("ntu-meta").textContent = meta;
  drawHistory(snap.history || [], on);

  const rate = formatRate(snap.oxygen_g_h || 0);
  document.getElementById("o2-rate").textContent = rate.value;
  document.getElementById("o2-unit").textContent = rate.unit;
  document.getElementById("o2-today").textContent = formatToday(snap.oxygen_today_g || 0);

  const pump = document.getElementById("pump-state");
  pump.textContent = snap.pump_on ? "Pompa in filtraggio" : "Pompa ferma";
  pump.classList.toggle("is-on", Boolean(snap.pump_on));
  document.getElementById("filter-reason").textContent =
    REASONS[snap.filter_reason] || snap.filter_reason || "";
  const dur = formatDuration(snap.state_age_s || 0);
  document.getElementById("filter-time").textContent = snap.pump_on
    ? "Accesa da " + dur
    : "Ferma da " + dur;

  let fault = "";
  if (snap.pump_error) fault = "Il relè non ha accettato il comando.";
  else if (!snap.sensor_ok) {
    fault = "Sensore di torbidità non leggibile. In automatico la pompa resta spenta.";
  }
  showFault(fault);

  const spoken = phase.label + ". " + (snap.pump_on ? "Pompa in filtraggio." : "Pompa ferma.");
  if (spoken !== lastSpoken) {
    liveEl.textContent = spoken;
    lastSpoken = spoken;
  }
}

async function poll() {
  if (busy) return;
  busy = true;
  try {
    const response = await fetch("/api/state", { cache: "no-store" });
    if (!response.ok) throw new Error(String(response.status));
    misses = 0;
    render(await response.json());
  } catch (err) {
    misses += 1;
    if (misses >= 2) showFault("Il controller non risponde.");
  } finally {
    busy = false;
  }
}

document.querySelectorAll(".actions button").forEach((button) => {
  button.addEventListener("click", async () => {
    const mode = button.dataset.mode;
    try {
      const response = await fetch("/api/pump", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mode }),
      });
      if (!response.ok) throw new Error("pump");
      misses = 0;
      render(await response.json());
    } catch (err) {
      showFault("Comando pompa non inviato.");
    }
  });
});

renderClock();
setInterval(renderClock, 1000);
poll();
setInterval(poll, 1000);
