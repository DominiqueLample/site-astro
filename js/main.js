/* SHO·astro — galerie pilotée par données + interactions.
   Pour remplacer les images de démo par vos propres photos :
   déposez vos fichiers dans assets/ et éditez le tableau PHOTOS ci-dessous. */

const PHOTOS = [
  {
    src: "assets/neb-coeur.jpg",
    alt: "Nébuleuse du Cœur, style SHO : cœur bleu-vert d'oxygène ionisé, halo vert d'hydrogène, lisières rouges de soufre",
    title: "IC 1805 — La Nébuleuse du Cœur",
    meta: ["Cassiopée", "≈ 7 500 a.l.", "Région H II", "SII 7 nm · Hα 6 nm · OIII 5 nm", "3 × 20 poses de 10 min"],
    comment: "Un vaste nuage d'hydrogène ionisé (région H II) sculpté par le rayonnement UV de l'amas ouvert Melotte 15, des étoiles O âgées de seulement 1 à 2 millions d'années. En SHO, le bleu d'[O III] marque le cœur très excité autour des étoiles les plus chaudes, le vert de Hα dessine la masse du nuage, et le rouge de [S II] souligne les lisières où le front d'ionisation heurte le gaz froid."
  },
  {
    src: "assets/neb-croissant.jpg",
    alt: "Nébuleuse du Croissant en arc, style SHO : coquille choquée rouge orangé et gaz interne vert bleuté",
    title: "NGC 6888 — La Nébuleuse du Croissant",
    meta: ["Cygne", "≈ 5 000 a.l.", "Bulle de vent stellaire", "SII 7 nm · Hα 6 nm · OIII 5 nm", "3 × 15 poses de 15 min"],
    comment: "Une coquille en arc produite par l'étoile de Wolf-Rayet WR 136 : son vent stellaire ultrarapide (≈ 1 700 km/s) rattrape et heurte l'enveloppe lente éjectée il y a ~ 250 000 ans. Le choc chauffe et comprime le gaz : c'est exactement ce que le canal rouge [S II] révèle en bord de coquille, tandis que Hα et [O III] tracent l'intérieur de la bulle."
  },
  {
    src: "assets/neb-rosette.jpg",
    alt: "Nébuleuse de la Rosette en anneau, style SHO : bord interne bleu d'oxygène, anneau vert d'hydrogène, extérieur rouge de soufre",
    title: "NGC 2237 — La Nébuleuse de la Rosette",
    meta: ["Licorne", "≈ 5 200 a.l.", "Nébuleuse à émission + amas", "SII 7 nm · Hα 6 nm · OIII 5 nm", "3 × 25 poses de 10 min"],
    comment: "L'amas NGC 2244, au centre de la rosette, souffle par son rayonnement et ses vents une cavité dans le nuage moléculaire géant. Le bord interne de l'anneau, directement exposé au UV des étoiles O, brille en [O III] (bleu) ; plus loin, Hα (vert) domine le gaz ionisé, et [S II] (rouge) apparaît aux lisières externes. Un bel exemple de photoévaporation : la nébuleuse se fait lentement dévorer de l'intérieur."
  },
  {
    src: "assets/neb-dumbbell.jpg",
    alt: "Nébuleuse de l'Haltère à deux lobes, style SHO : lobes bleu-vert d'oxygène, barre centrale verdâtre d'hydrogène, bords rougeâtres de soufre",
    title: "M27 — La Nébuleuse de l'Haltère",
    meta: ["Petit Renard", "≈ 1 360 a.l.", "Nébuleuse planétaire", "SII 7 nm · Hα 6 nm · OIII 5 nm", "3 × 12 poses de 8 min"],
    comment: "Il y a environ 10 000 ans, une étoile géante rouge a expulsé ses couches externes, formant cette nébuleuse planétaire en forme d'haltère. Le cœur reste est une naine blanche très chaude (> 80 000 K) dont le rayonnement UV ionise le gaz éjecté : [O III] (bleu) domine là où le gaz est le plus excité, Hα (vert) trace l'hydrogène ionisé, et [S II] (rouge) colore les zones de plus basse ionisation. Le Soleil finira comme ça dans ~ 5 milliards d'années."
  }
];

/* ---------- galerie ---------- */
function renderGallery() {
  const gallery = document.getElementById("gallery");
  gallery.innerHTML = PHOTOS.map((p, i) => `
    <article class="photo reveal" data-index="${i}">
      <figure>
        <img src="${p.src}" alt="${p.alt}" loading="lazy">
        <span class="zoom">⤢ agrandir</span>
      </figure>
      <div class="photo-body">
        <h3>${p.title}</h3>
        <div class="meta">${p.meta.map(m => `<span>${m}</span>`).join("")}</div>
        <p class="comment"><strong>Commentaire astrophysique —</strong> ${p.comment}</p>
      </div>
    </article>`).join("");
}

/* ---------- lightbox ---------- */
function initLightbox() {
  const lb = document.getElementById("lightbox");
  const img = document.getElementById("lb-img");
  const title = document.getElementById("lb-title");
  const comment = document.getElementById("lb-comment");

  document.getElementById("gallery").addEventListener("click", (e) => {
    const card = e.target.closest(".photo");
    if (!card) return;
    const p = PHOTOS[Number(card.dataset.index)];
    img.src = p.src;
    img.alt = p.alt;
    title.textContent = p.title;
    comment.textContent = p.comment;
    lb.hidden = false;
    document.body.style.overflow = "hidden";
  });

  const close = () => { lb.hidden = true; document.body.style.overflow = ""; };
  lb.addEventListener("click", close);
  lb.querySelector(".lb-close").addEventListener("click", (e) => { e.stopPropagation(); close(); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape" && !lb.hidden) close(); });
}

/* ---------- champ d'étoiles animé ---------- */
function initStarfield() {
  const canvas = document.getElementById("stars");
  const ctx = canvas.getContext("2d");
  let stars = [];
  let w, h, raf;

  function resize() {
    const hero = canvas.parentElement;
    w = canvas.width = hero.clientWidth;
    h = canvas.height = hero.clientHeight;
    const n = Math.min(320, Math.floor((w * h) / 6500));
    stars = Array.from({ length: n }, () => ({
      x: Math.random() * w,
      y: Math.random() * h,
      r: Math.random() * 1.4 + 0.3,
      phase: Math.random() * Math.PI * 2,
      speed: 0.4 + Math.random() * 1.2,
      tint: Math.random()
    }));
  }

  function draw(t) {
    ctx.clearRect(0, 0, w, h);
    for (const s of stars) {
      const a = 0.35 + 0.65 * (0.5 + 0.5 * Math.sin(t / 1000 * s.speed + s.phase));
      ctx.beginPath();
      ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
      ctx.fillStyle = s.tint < 0.15
        ? `rgba(170,220,255,${a})`
        : s.tint < 0.3
          ? `rgba(255,220,190,${a})`
          : `rgba(255,255,255,${a})`;
      ctx.fill();
    }
    raf = requestAnimationFrame(draw);
  }

  resize();
  window.addEventListener("resize", resize);
  raf = requestAnimationFrame(draw);
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) cancelAnimationFrame(raf);
    else raf = requestAnimationFrame(draw);
  });
}

/* ---------- spectre : isoler un canal ---------- */
function initSpectrum() {
  const svg = document.getElementById("spectrum");
  const chips = document.querySelectorAll(".chip");
  if (!svg) return;

  function setActive(key) {
    const anyActive = [...chips].some(c => c.classList.contains("active"));
    svg.classList.toggle("dim", anyActive);
    svg.querySelectorAll(".line, .band").forEach(el => {
      el.classList.toggle("active", key !== null && el.dataset.key === key);
    });
  }

  chips.forEach(chip => {
    chip.addEventListener("click", () => {
      const key = chip.dataset.key;
      const wasActive = chip.classList.contains("active");
      chips.forEach(c => c.classList.remove("active"));
      if (wasActive) { setActive(null); return; }
      chip.classList.add("active");
      setActive(key);
    });
  });
}

/* ---------- apparition au scroll ---------- */
function initReveal() {
  const obs = new IntersectionObserver((entries) => {
    entries.forEach(en => {
      if (en.isIntersecting) { en.target.classList.add("visible"); obs.unobserve(en.target); }
    });
  }, { threshold: 0.12 });
  document.querySelectorAll(".reveal").forEach(el => obs.observe(el));
}

document.addEventListener("DOMContentLoaded", () => {
  renderGallery();
  initLightbox();
  initStarfield();
  initSpectrum();
  initReveal();
});
