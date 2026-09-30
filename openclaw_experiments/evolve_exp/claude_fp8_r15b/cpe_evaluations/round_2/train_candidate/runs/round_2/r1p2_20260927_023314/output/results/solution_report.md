# Solution

## Subtask 1: Part I (a): For a 100 W HF constant-carrier signal below the MUF from a point source on land, determine the strength of 

### Problem

Part I (a): For a 100 W HF constant-carrier signal below the MUF from a point source on land, determine the strength of the first reflection off a turbulent ocean (after one ionospheric reflection) and compare it with the first reflection off a calm ocean.

### Analysis

Assumptions: (1) operating frequency FOT = 0.85*MUF = 6 MHz with MUF ~ 7 MHz (external data item 2, ITU-R P.531); (2) first ionospheric hop covers a ground arc of 2000 km (typical HF skywave hop); (3) effective virtual height 600 km for oblique F2 use; (4) seawater complex permittivity from the modified Debye model (external data item 1, Meissner et al. 2004), with ionic conductivity dominant at 6 MHz; (5) turbulence modelled as a Gaussian facet-slope ensemble with significant wave height Hs = 3 m and correlation length 200 m (stormy sea); (6) calm ocean = flat interface (Hs = 0); (7) receiver bandwidth 3 kHz (standard HF voice/data channel); (8) thermal noise floor at 290 K. Method: small-patch perturbed-incidence framework (expert round 1): per-facet Fresnel reflection at the perturbed local incidence angle, ensemble-averaged, plus a diffuse Bragg-type scattered term. Path loss: free-space spreading over the total slant path (2 x slant per hop), ITU-R P.531-style ionospheric absorption, and a 2 dB refraction loss.

### Modeling Process

Seawater permittivity (modified Debye, 35 ppt, 15 C): eps = eps_inf + (eps_s - eps_inf)/(1 - (i f/f0)^alpha) + i sigma_d/(2 pi f eps0), with eps_s = 80, eps_inf = 4.9, f0 = 24.9 kHz, alpha = 0.90, sigma_d = 4 S/m. At 6 MHz: |eps_r| ~ 10^3 (ionic term dominates). Fresnel |Gamma|^2 at incidence angle theta_i (from normal): for s-pol, |Gamma_s|^2 = |(n cos(theta_i) - t)/(n cos(theta_i) + t)|^2 where n = sqrt(eps_r), t = sqrt(1 - sin^2(theta_i)/n^2); for p-pol, |Gamma_p|^2 = |(sin^2(theta_i)/n^2 - cos(theta_i)*t)/(sin^2(theta_i)/n^2 + cos(theta_i)*t)|^2; average of both. Small-patch ensemble: E[|Gamma(theta_i + delta)|^2] over delta ~ N(0, s^2/2) where s = sqrt(sigma_s^2) is the mean facet slope, sigma_s^2 = (2 pi/L_cor)^2 * Hs^2 / 8. Coherent suppression: exp(-2 (k s cos(theta_i))^2). Diffuse term: sigma0 * (1 + 5 k s), bounded at 0.05. Total reflection coefficient R = R_specular + R_diffuse. Path loss per hop: PL = (c/(4 pi f * 2*slant))^2 * 10^(-A_ion/10) * 10^(-A_ref/10), where slant = sqrt(hv^2 + (d/2)^2), A_ion = A0(f) (d/1000 km)^0.6 dB with A0(7 MHz) = 2 dB, A_ref = 2 dB. Received power: P = P_t * PL * R_ocean. SNR = 10 log10(P / kTB), B = 3 kHz.

### Outcome Analysis

At 6 MHz, incidence angle 59.0 deg (from normal), Hs = 3 m, L = 200 m: R_smooth_calm = 0.9755 (-0.11 dB), R_calm_total = 0.9855 (-0.06 dB), R_turb_specular = 0.9755 (-0.11 dB), R_turb_total = 0.9857 (-0.06 dB). The turbulent ocean reflection is +0.0007 dB relative to the calm ocean. Power at the ocean after one iono hop: 9.801e-11 W. Reflected power (turbulent): 9.660e-11 W, SNR = 69.05 dB. Reflected power (calm): 9.659e-11 W, SNR = 69.05 dB. The difference is negligible (~0.001 dB) because at 59 deg from normal the Fresnel coefficient for seawater is already close to 1, so the perturbation from turbulence has a small effect on the coherent reflection. The empirical finding that turbulent ocean attenuates more is likely due to additional mechanisms (absorption by the rough surface, scattering into the ionosphere) not captured by the simple small-patch model. Limitations: (1) the Debye model parameters are for 15 C, 35 ppt; (2) the wave spectrum is approximated by an exponential (short) spectrum; (3) the diffuse scattering coefficient is a fixed parameter, not derived from the full Bragg integral.

## Subtask 2: Part I (b): If additional reflections (2 through n) take place off calm oceans, what is the maximum number of hops the s

### Problem

Part I (b): If additional reflections (2 through n) take place off calm oceans, what is the maximum number of hops the signal can take before its strength falls below a usable SNR threshold of 10 dB?

### Analysis

The signal propagates through successive ionospheric hops, each reflecting off a calm ocean. The cumulative path loss per hop (free-space spreading + iono absorption + refraction) is ~119 dB for a 2000 km hop at 6 MHz. The ocean reflection loss is ~0.1 dB per hop (R_calm ~ 0.976). The signal is received at a remote receiver after n hops; the SNR is measured at that receiver in a 3 kHz bandwidth. The maximum n is found by requiring SNR(n) >= 10 dB.

### Modeling Process

Per-hop loss factor: L_hop = (c/(4 pi f * 2*slant))^2 * 10^(-A_ion/10) * 10^(-A_ref/10). For d = 2000 km, hv = 600 km: slant = sqrt(600^2 + 1000^2) = 1166 km, total_path = 2332 km. L_hop = (3e8/(4 pi * 6e6 * 2.332e6))^2 * 10^(-2.6/10) * 10^(-2/10) = (1.7e-6)^2 * 0.55 * 0.63 = 2.9e-12 * 0.347 = 1.0e-12. Cumulative power after n hops: P(n) = P_t * L_hop^n * R_calm^(n-1). SNR(n) = 10 log10(P(n) / kTB). Find max n with SNR(n) >= 10 dB.

### Outcome Analysis

SNR after hop 1: 69.12 dB (above 10 dB threshold). SNR after hop 2: -51.08 dB (below 10 dB threshold). Therefore the maximum number of total hops is 1 (the first iono hop to the first ocean reflection), and the maximum number of additional calm-ocean reflections is 0. The 100 W isotropic point source is not sufficient to sustain multi-hop propagation over 2000 km hops; the per-hop path loss (~119 dB) is much larger than the ocean reflection gain (~0 dB), so the signal drops below the noise floor after 2 hops. This highlights the need for more powerful transmitters, directional antennas, or shorter hops for multi-hop HF communication. Limitations: (1) the free-space spreading model is a conservative estimate; the actual ionospheric refraction focuses the wave and reduces the effective path loss; (2) the 3 kHz bandwidth is assumed; a narrower bandwidth would give a lower noise floor and allow more hops.

## Subtask 3: Part II: How do the Part I findings compare with HF reflections off mountainous or rugged terrain versus smooth terrain?

### Problem

Part II: How do the Part I findings compare with HF reflections off mountainous or rugged terrain versus smooth terrain?

### Analysis

Per expert round 3, the same small-patch framework is applied to terrain as a lossy dielectric (soil) with roughness statistics. Smooth terrain = flat soil interface with a single Fresnel coefficient from the frequency-dependent complex soil permittivity/conductivity. Rugged terrain = the same interface with a height/slope distribution (slope variance from a relief parameter), ensemble-averaged, plus a diffuse scattered-loss term. Soil dielectric values: wet soil (eps_r = 28, sigma = 0.03 S/m), dry soil (eps_r = 9, sigma = 0.003 S/m). Ruggedness: 30 m relief over ~500 m scale => slope variance ~ 0.004.

### Modeling Process

Soil permittivity: eps = eps_r + i sigma/(2 pi f eps0). At 6 MHz: wet soil |eps_r| ~ 10^3 (ionic term dominates), dry soil |eps_r| ~ 10^2. Fresnel |Gamma|^2 at incidence angle theta_i (same as Part I). Small-patch ensemble: same as Part I, with slope variance from the terrain roughness. Diffuse term: sigma0 * (1 + 5 k s), bounded at 0.05. Results: R_smooth_wet_soil = 0.7541, R_rugged_wet_soil = 0.7531, R_smooth_dry_soil = 0.4280, R_calm_ocean = 0.9755.

### Outcome Analysis

The calm ocean reflects 1.12 dB better than smooth wet soil and 3.58 dB better than smooth dry soil. This is because seawater has a higher effective permittivity at HF (ionic conductivity term) than soil, giving a Fresnel coefficient closer to 1. Rugged terrain shifts the reflection coefficient by -0.0055 dB relative to smooth wet soil — a negligible effect, for the same reason as in Part I: at 59 deg from normal the Fresnel coefficient is already close to 1, so the perturbation from roughness has a small effect on the coherent reflection. The ocean-vs-terrain contrast is dominated by the dielectric properties (permittivity and conductivity), not the roughness. Limitations: (1) soil dielectric values are representative, not site-specific; (2) the roughness parameter is a single slope variance, not a full terrain spectrum; (3) the model does not account for shadowing or diffraction around terrain features.

## Subtask 4: Part III: A ship travelling across the ocean will use HF for communications and to receive weather and traffic reports. 

### Problem

Part III: A ship travelling across the ocean will use HF for communications and to receive weather and traffic reports. How does your model change to accommodate a shipboard receiver moving on a turbulent ocean? How long can the ship remain in communication using the same multi-hop path?

### Analysis

Per expert round 2, the primary answer is statistical: the ship keeps the same multi-hop path structure, but the moving receiver sweeps through a time-varying facet field, so the turbulent-ocean reflection loss is a random process. The answer is the time until the SNR (or a specified fade depth, e.g. 1% of time) falls below the 10 dB threshold, computed from ship speed, facet correlation length, and available SNR margin. The geometry window (deterministic bound on how long the path can be re-anchored) is reported as a secondary quantity. Assumptions: ship speed 15 kn (~7.7 m/s), turbulent ocean Hs = 3 m, L = 200 m, Rician fading with K = 6 dB (diffuse floor + specular).

### Modeling Process

Mean SNR at the receiver after N hops: SNR_mean = 10 log10(P_mean / kTB), where P_mean is the mean received power (using the mean ocean reflection fraction R_spec). The instantaneous reflected power follows a Rician distribution with K-factor K = 6 dB (from the diffuse floor). The probability that the instantaneous power falls below the 10 dB threshold: P_below = CDF_Rician(P_threshold / P_mean). Fade rate: f_d = v_ship / (2 * L_cor) (fades per second, correlation length L_cor). Level-crossing rate at the threshold: LCR = f_d * sqrt(2 ln(1/P_below)). Mean time to first outage: t_fade = 1/LCR. Secondary geometry window: t_geom = seg / v_ship, where seg is the hop ground distance.

### Outcome Analysis

Mean SNR at the receiver: 69.01 dB. Probability of being below the 10 dB threshold: 0.0000. Fade rate: 0.0193 Hz. Level-crossing rate: 0.1011 per second. Mean time to first outage (primary, statistical): 9.9 s. Secondary geometry window: 259179 s (~72.0 h). The ship remains in communication for about 0.0 h on the same multi-hop path before the first deep fade drops the SNR below 10 dB. The geometry window is much longer, so the statistical fade is the dominant limitation. Limitations: (1) the Rician K-factor is a fixed parameter, not derived from the wave spectrum; (2) the model assumes the path structure remains valid (no re-anchoring); (3) the ship speed is constant; (4) the model does not account for ionospheric variability (MUF changes with time of day, season, solar activity).

## Subtask 5: Part IV: Prepare a short (1 to 2 pages) synopsis of your results suitable for publication as a short note in IEEE Commun

### Problem

Part IV: Prepare a short (1 to 2 pages) synopsis of your results suitable for publication as a short note in IEEE Communications Magazine.

### Analysis

The synopsis summarises the key findings from Parts I-III in a concise, publication-ready format. It highlights the small-patch perturbed-incidence framework, the key quantitative results, and the practical implications for HF ocean communication.

### Modeling Process

The synopsis is a narrative summary of the results, not a mathematical derivation. It is included in the subtask_outcome_analysis field below.

### Outcome Analysis

We model HF multi-hop propagation with ocean reflections using a small-patch perturbed-incidence framework: turbulence is a Gaussian facet-slope ensemble (variance from significant wave height and correlation length), with per-facet Fresnel reflection at the modified-Debye seawater permittivity (Meissner et al., 2004) and a diffuse Bragg-type scattered term. For a 100 W constant carrier at FOT = 0.85*MUF = 6 MHz (MUF ~ 7 MHz) with a 4000 km first ionospheric hop onto a stormy sea (Hs = 3 m, L ~ 200 m), the first ocean reflection strength is 0.00 dB different from the calm-ocean value. Calm-ocean hops sustain 1 total hops before SNR < 10 dB. Rugged soil terrain shifts the reflection coefficient by 0.01 dB relative to smooth wet soil; the calm ocean reflects 1.1 dB better than smooth wet soil. A ship at 15 kn on the turbulent ocean retains the same multi-hop path statistically for about 10 s (primary, fade limited), with a deterministic geometry window of 259179 s (secondary bound).

---

_Rendered by the Claude Code backend from `solution.json`; the JSON container is the submission of record._
