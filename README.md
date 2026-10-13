# bio-quantum-axon-lindblad
Computational model of a myelinated axon as an open quantum system at 310K using Lindblad master equation (QuTiP).

# V148-SISTEMA-TOTAL — Quantum dynamics of the myelinated axon at 310 K

**Languages / Idiomas / Idiomes:** [English](#english) · [Español](#español) · [Català](#català)

Reproducibility repository for the preprint *"Quantum Entanglement and Coherent Information Transfer in a Myelinated Axon at Physiological Temperature: a 159-step auditable open-quantum-system model"* (bioRxiv, DOI pending).

---

## English

### Key results (run 2026-10-13)
| Metric | Value | Meaning |
|---|---|---|
| Response 1-1 (R_11) | 1.0 | Conditional gate closes the cycle exactly |
| Bit ratio ON/OFF | 10.33 | Robust binary discrimination of the vacuum channel |
| Chain efficiency η | 0.9697 | F_phase × F_water × T_lock |
| Fidelity M1 (PST) | 0.999888 | Perfect state transfer without intermediate readout |
| Trace error | ≤ 4.4e-16 | Probability conservation at machine precision |
| Min eig(ρ) | ≥ −5.3e-17 | Positivity maintained |
| Coherent stock | 4×10¹² bits | Brain-scale estimate (2×10¹² cavities × 2 bits) |
| Fill time 10⁹ bits | 9.05 ms | Coherent writing speed |

### The 13-layer audited chain
Metabolism → biophoton (UPE) → Casimir cavity (myelin) → harmonics n=1..6 → photon–phonon phase → phonon–water → Dicke triads → 2:1 magic dial → backdoor gate → M1 channel (PST) → ON/OFF dynamics → QuTiP validation → 1-1 closure.
Every step is logged as **formula + value + unit + tool + reference**: 159 steps in `v148_output/v148_registro_pasos_*.csv`.

### Repository contents
```text
├── v148_sistema_total.py            # Full 13-layer engine (159 audited steps)
├── v148_output/
│   ├── v148_registro_pasos_*.csv    # Step-by-step audit trail
│   ├── v148_dyn_ON_*.csv            # 1500 ns dynamics, gate OPEN
│   ├── v148_dyn_OFF_*.csv           # 1500 ns dynamics, gate CLOSED
│   ├── v148_reporte_*.txt           # Human-readable full report
│   └── v148_sistema_total_*.png     # 16-panel validation dashboard
└── README.md                        # This trilingual document
```

### Reproduce
```bash
pip install numpy scipy matplotlib pandas qutip
python3 v148_sistema_total.py
```
Outputs appear in `v148_output/`. Runtime < 2 min on a single-board computer.

### Falsifiable predictions
1. Post-stimulus delta–theta phase re-engagement in healthy subjects (high-density EEG, 128–256 channels).
2. Absent re-engagement in early multiple sclerosis without visible MRI lesions.
3. Higher spectral coherence at rest than during intense cognitive task.
4. Matching lipid/axoplasm refractive indices abolishes coherent transport ex vivo, sparing ionic conduction.
5. Disorganizing myelin helicity breaks delta–theta locking without anatomically visible damage.

**Falsification criterion:** if (1) fails in healthy controls, or (2) shows normal re-engagement in early MS, the core model is abandoned or reformulated. Accepted in advance.

### Honest audit: foundation, wall, roof
- **Foundation** (physics proven elsewhere): Lindblad master equation, cavity optomechanics, Dicke superradiance, perfect-state-transfer protocol, Landauer limit.
- **Wall** (biology measured by others, cited): myelin as optical waveguide (Zeng 2022; Kumar 2016; Frede 2023); active interfacial water (Bae 2025; Bolmatov 2026); myelin and long-term memory (Fields 2020); phase–amplitude coupling as biomarker (van der Meij 2012; Lega 2016; Adams 2019).
- **Roof** (declared open hypotheses): coherence sustained across a full internode in warm tissue; myelin as coherent resonator in vivo; angular zero point as condition of experiential unity.
- **Known errors, corrected or declared:** static Casimir scale error (corrected); 1.1° angle as graphene analogy, not morphology (declared); oligodendrocyte core mode as slow collective variable, not quantum DNA vibration (declared).

### Philosophy
- **Popcorn:** let the data pop on their own. No forcing, no mid-run intervention; crashes and refutations are the method, not obstacles.
- **Proletarian science:** runs on a single-board computer (Orange Pi 5B) with free software; open CSVs anyone can review, repeat and contradict. No black box.
- **Grinberg heritage:** take seriously inter-brain correlations and the intuition of a brain coupled to a field that exceeds it; translate them into measurable correlates. Inherit with respect, correct with respect.
- **No revenge:** the model is built against no one. If it ever matters, it will be because many people contributed a little.

---

## Español

### Resultados clave (corrida 2026-10-13)
| Métrica | Valor | Significado |
|---|---|---|
| Respuesta 1-1 (R_11) | 1.0 | La puerta condicional cierra el ciclo exactamente |
| Ratio de bits ON/OFF | 10.33 | Discriminación binaria robusta del canal de vacío |
| Eficiencia de cadena η | 0.9697 | F_fase × F_agua × T_lock |
| Fidelidad M1 (PST) | 0.999888 | Transporte de estado perfecto sin lectura intermedia |
| Error de traza | ≤ 4.4e-16 | Conservación de probabilidad a precisión de máquina |
| Autovalor mín. de ρ | ≥ −5.3e-17 | Positividad mantenida |
| Estoc coherente | 4×10¹² bits | Estimación a escala cerebral (2×10¹² cavidades × 2 bits) |
| Tiempo de llenado 10⁹ bits | 9.05 ms | Velocidad de escritura coherente |

### La cadena auditada de 13 capas
Metabolismo → biofotón (UPE) → cavidad Casimir (mielina) → armónicos n=1..6 → fase fotón–fonón → fonón–agua → triadas Dicke → dial mágico 2:1 → puerta trasera → canal M1 (PST) → dinámica ON/OFF → validación QuTiP → cierre 1-1.
Cada paso queda registrado como **fórmula + valor + unidad + herramienta + referencia**: 159 pasos en `v148_output/v148_registro_pasos_*.csv`.

### Reproducir
```bash
pip install numpy scipy matplotlib pandas qutip
python3 v148_sistema_total.py
```

### Predicciones falsables
1. Reenganche delta–theta post-estímulo en sujetos sanos (EEG de alta densidad).
2. Ausencia de reenganche en esclerosis múltiple temprana sin lesiones visibles en RMN.
3. Coherencia espectral mayor en reposo que durante tarea cognitiva intensa.
4. Igualar los índices de refracción lípido/axoplasma abole el transporte coherente ex vivo sin tocar la conducción iónica.
5. Desorganizar la helicidad de la mielina rompe el enganche delta–theta sin daño anatómico visible.

**Criterio de refutación:** si (1) falla en controles sanos o (2) muestra reenganche normal en EM temprana, el núcleo del modelo se abandona o reformula. Aceptado de antemano.

### Auditoría honesta: cimiento, pared y tejado
- **Cimiento** (física probada fuera): ecuación maestra de Lindblad, optomecánica de cavidades, superradiancia de Dicke, protocolo PST, límite de Landauer.
- **Pared** (biología medida por otros, citada): mielina como guía de onda (Zeng 2022; Kumar 2016; Frede 2023); agua interfacial activa (Bae 2025; Bolmatov 2026); mielina y memoria (Fields 2020); acoplamiento fase-amplitud como biomarcador (van der Meij 2012; Lega 2016; Adams 2019).
- **Tejado** (hipótesis abiertas declaradas): coherencia sostenida en un internodo completo en tejido caliente; mielina como resonador coherente in vivo; punto cero angular como condición de unidad experiencial.
- **Errores conocidos, corregidos o declarados:** error de escala del Casimir estático (corregido); ángulo de 1.1° como analogía de grafeno, no morfología (declarado); modo del núcleo oligodendrocito como variable colectiva lenta, no vibración cuántica del ADN (declarado).

### Filosofía
- **Palomitas:** dejar que los datos salgan solos. Sin forzar, sin intervenir a mitad de corrida; los cuelgues y refutaciones son el método, no obstáculos.
- **Ciencia proletaria:** corre en un ordenador de una sola placa (Orange Pi 5B) con software libre; CSVs abiertos que cualquiera puede revisar, repetir y contradecir. Sin caja negra.
- **Herencia Grinberg:** tomar en serio la correlación inter-cerebral y la intuición de un cerebro acoplado a un campo que lo excede; traducirlas a correlatos medibles. Heredar con respeto, corregir con respeto.
- **Sin venganza:** el modelo no se construye contra nadie. Si algún día vale algo, será porque mucha gente puso un poco.

---

## Català

### Resultats clau (corrida 2026-10-13)
| Mètrica | Valor | Significat |
|---|---|---|
| Resposta 1-1 (R_11) | 1.0 | La porta condicional tanca el cicle exactament |
| Ràtio de bits ON/OFF | 10.33 | Discriminació binària robusta del canal de buit |
| Eficiència de cadena η | 0.9697 | F_fase × F_aigua × T_lock |
| Fidelitat M1 (PST) | 0.999888 | Transport d'estat perfecte sense lectura intermèdia |
| Error de traça | ≤ 4.4e-16 | Conservació de probabilitat a precisió de màquina |
| Autovalor mín. de ρ | ≥ −5.3e-17 | Positivitat mantinguda |
| Estoc coherent | 4×10¹² bits | Estimació a escala cerebral (2×10¹² cavitats × 2 bits) |
| Temps d'ompliment 10⁹ bits | 9.05 ms | Velocitat d'escriptura coherent |

### La cadena auditada de 13 capes
Metabolisme → biofotó (UPE) → cavitat Casimir (mielina) → harmònics n=1..6 → fase fotó–fonó → fonó–aigua → tríades Dicke → dial màgic 2:1 → porta del darrere → canal M1 (PST) → dinàmica ON/OFF → validació QuTiP → tancament 1-1.
Cada pas queda registrat com a **fórmula + valor + unitat + eina + referència**: 159 passos a `v148_output/v148_registro_pasos_*.csv`.

### Reproduir
```bash
pip install numpy scipy matplotlib pandas qutip
python3 v148_sistema_total.py
```

### Prediccions falsables
1. Reenganxament delta–theta post-estímul en subjectes sans (EEG d'alta densitat).
2. Absència de reenganxament en esclerosi múltiple primerenca sense lesions visibles a la RMN.
3. Coherència espectral més alta en repòs que durant tasca cognitiva intensa.
4. Igualar els índexs de refracció lípid/axoplasma abolix el transport coherent ex vivo sense tocar la conducció iònica.
5. Desorganitzar l'helicitat de la mielina trenca l'enganxament delta–theta sense dany anatòmic visible.

**Criteri de refutació:** si (1) falla en controls sans o (2) mostra reenganxament normal en EM primerenca, el nucli del model s'abandona o es reformula. Acceptat d'avançada.

### Auditoria honesta: fonament, paret i teulada
- **Fonament** (física provada altrament): equació mestra de Lindblad, optomecànica de cavitats, superradiància de Dicke, protocol PST, límit de Landauer.
- **Paret** (biologia mesurada per altres, citada): mielina com a guia d'ona (Zeng 2022; Kumar 2016; Frede 2023); aigua interfacial activa (Bae 2025; Bolmatov 2026); mielina i memòria (Fields 2020); acoblament fase-amplitud com a biomarcador (van der Meij 2012; Lega 2016; Adams 2019).
- **Teulada** (hipòtesis obertes declarades): coherència sostinguda en un internode complet en teixit calent; mielina com a ressonador coherent in vivo; punt zero angular com a condició d'unitat experiencial.
- **Errors coneguts, corregits o declarats:** error d'escala del Casimir estàtic (corregit); angle d'1.1° com a analogia de grafè, no morfologia (declarat); mode del nucli oligodendrocit com a variable col·lectiva lenta, no vibració quàntica de l'ADN (declarat).

### Filosofia
- **Crispetes:** deixar que les dades surtin soles. Sense forçar, sense intervenir a mitja corrida; les penjades i refutacions són el mètode, no obstacles.
- **Ciència proletària:** corre en un ordinador d'una sola placa (Orange Pi 5B) amb programari lliure; CSV oberts que qualsevol pot revisar, repetir i contradir. Sense caixa negra.
- **Herència Grinberg:** prendre seriosament la correlació inter-cerebral i la intuïció d'un cervell acoblat a un camp que l'excedeix; traduir-les a correlats mesurables. Heretar amb respecte, corregir amb respecte.
- **Sense venjança:** el model no es construeix contra ningú. Si algun dia val alguna cosa, serà perquè molta hi ha posat una mica.

---

## Citation / Citación / Citació

```bibtex
@misc{alfonso2026v148,
  title  = {V148-SISTEMA-TOTAL: Quantum dynamics of the myelinated axon at 310 K.
            A 159-step auditable open-quantum-system chain},
  author = {Alfonso, M.},
  year   = {2026},
  howpublished = {\url{https://github.com/infotecnova06-lgtm/bio-quantum-axon-lindblad}}
}
```

**License / Licencia / Llicència:** CC-BY 4.0 (dades, text i codi / data, text and code). **No competing interests / Sin intereses en competencia / Sense interessos en competència.**

*Y en la senda nos encontraremos. / I ens trobarem en el camí. / And on the path we shall meet.*
