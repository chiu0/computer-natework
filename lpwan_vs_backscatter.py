"""
================================================================================
LPWAN (LoRa) vs Backscatter 비교 시뮬레이션
================================================================================

이 코드의 모든 수식과 파라미터는 아래 참고문헌(IEEE 인용 형식)을 기반으로
하며, 각 항목은 1차 출처(논문 원전/데이터시트/표준 교과서)에서 직접 대조하여
검증하였다. 함수 docstring과 파라미터 주석에 해당 출처를 [N]으로 표기한다.

--------------------------------------------------------------------------------
수식 / 파라미터별 출처 요약  (★ = 1차 출처 직접 대조 완료)
--------------------------------------------------------------------------------
  [1]★ Log-distance 경로손실   PL(d)=PL(d0)+10n*log10(d/d0)
        - Rappaport, Eq.(3.93)에서 직접 확인 (섀도잉 항 Xσ는 생략)
  [2]★ Backscatter dyadic 채널  왕복 경로 -> 경로손실 지수 2배 (r^4 감쇠)
        - Griffin & Durgin, Eq.(2) 및 "scattered power falls off as r^4"에서 확인
  [3]★ LoRa 수신감도            SX1276 @SF12, BW=125kHz = -136 dBm
        - Semtech SX1276 데이터시트, Table RFS_L125_HF에서 직접 확인
  [4]★ BER (BPSK/AWGN)          Pb=Q(sqrt(2Eb/N0))=0.5*erfc(sqrt(SNR))
        - Proakis & Salehi, Eq.(4.3-13)에서 직접 확인
  [5]★ Pure ALOHA 처리량        S=G*exp(-2G)  (원전 표기: rτ=Rτ*exp(-2Rτ))
        - Abramson, Eq.(2)에서 직접 확인 (G≡Rτ, S≡rτ; 최댓값 1/2e=0.184)
  [6]★ 열잡음 / 송신전력        N0=-174 dBm/Hz, EU 송신전력 14 dBm
        - Roehrig et al.(2025)에서 직접 확인; 열잡음 원 출처는 ITU-R P.1238
  [7]★ 자유공간 경로손실 상수   Lbf=20log(4πd/λ) → Hz/m 단위 전개 시 상수 -147.55
        - ITU-R P.525-3, Eq.(3)에서 직접 확인

--------------------------------------------------------------------------------
References (IEEE format)
--------------------------------------------------------------------------------
[1] T. S. Rappaport, Wireless Communications: Principles and Practice, 2nd ed.
    Upper Saddle River, NJ, USA: Prentice Hall, 2002, Sec. 3.11.3, Eq. (3.93).
[2] J. D. Griffin and G. D. Durgin, "Complete link budgets for backscatter-radio
    and RFID systems," IEEE Antennas Propag. Mag., vol. 51, no. 2, pp. 11-25,
    Apr. 2009, Sec. 3.2, Eq. (2).
[3] Semtech Corporation, "SX1276/77/78/79 - 137 MHz to 1020 MHz Low Power Long
    Range Transceiver," SX1276/77/78/79 Datasheet, Rev. 7, Camarillo, CA, USA,
    May 2020, Table "RFS_L125_HF".
[4] J. G. Proakis and M. Salehi, Digital Communications, 5th ed. New York, NY,
    USA: McGraw-Hill, 2008, Eq. (4.3-13).
[5] N. Abramson, "The ALOHA system: Another alternative for computer
    communications," in Proc. AFIPS Fall Joint Comput. Conf., vol. 37, 1970,
    pp. 281-285, Eq. (2).
[6] C. Roehrig, D. Hess, and B. H. D. Trinh, "System design for distributed
    energy management using multiple LPWAN technologies," in Proc. IECON 2025 -
    51st Annu. Conf. IEEE Ind. Electron. Soc., 2025.
[7] Recommendation ITU-R P.525-3, "Calculation of free-space attenuation,"
    ITU-R, Geneva, Switzerland, Sep. 2016, Annex 1, Eq. (3).

참고: 본 모델은 위 1차 출처의 핵심 수식을 채택하되, 시뮬레이션 단순화를 위해
일부 항(섀도잉 Xσ, backscatter 변조계수 M·편파 X·페이딩 마진 F2 등)은
고정 손실값으로 통합하거나 생략하였다. 자세한 내용은 각 함수 주석 참조.
================================================================================
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erfc

# ==============================================================================
# 0. 공통 물리 상수 및 시스템 파라미터
# ==============================================================================
C = 3e8  # 빛의 속도 (m/s)

# --- 주파수 (둘 다 sub-GHz ISM 대역 가정: 868 MHz) ---
FREQ_HZ = 868e6  # 유럽 ISM 대역 [6]

# --- 열잡음 기준 [6] ---
NOISE_FLOOR_DBM_PER_HZ = -174.0  # 열잡음 밀도 N0, 290K 기준 [6] (ITU-R P.1238)
NOISE_FIGURE_DB = 6.0            # 수신기 잡음지수 NF (SX1276 데이터시트 [3])

# --- LoRa (LPWAN) 파라미터 ---
LORA_TX_PWR_DBM = 14.0      # EU 868MHz 송신전력 규제 한도 14 dBm [6]
LORA_BW_HZ = 125e3          # 125 kHz (LoRaWAN 표준 대역폭)
LORA_SENSITIVITY_DBM = -136.0  # SX1276 @SF12, BW=125kHz [3] (Table RFS_L125_HF)
LORA_TX_ANT_GAIN_DBI = 2.0  # 가정값 (소형 노드 안테나)
LORA_RX_ANT_GAIN_DBI = 2.0  # 가정값

# --- Backscatter 파라미터 [2] ---
# 주의: backscatter 태그는 자체 송신을 안 하고 reader의 반송파를 반사함.
BACK_CARRIER_PWR_DBM = 30.0   # Reader 반송파(carrier) 전력 (~1W), 가정값
BACK_BW_HZ = 2e6              # 광대역 backscatter 가정 대역폭
BACK_TAG_GAIN_DBI = 1.0      # 가정값 (소형 태그 안테나)
BACK_READER_GAIN_DBI = 6.0   # 가정값 (고정형 reader 안테나, 이득 큼)
# 변조계수 M, 편파 X, 페이딩 마진 F2 등을 통합한 단일 손실값 (가정값) [2]
BACK_MODULATION_LOSS_DB = 10.0
BACK_SENSITIVITY_DBM = -90.0  # commodity reader 수신 감도 (보수적 가정값)

# 경로 손실 지수 n [1] (Rappaport Eq.3.93의 n)
PATH_LOSS_EXPONENT = 2.7   # 교외/준도심 환경 가정 (자유공간 2 ~ 실내 3~5 사이)


# ==============================================================================
# 1. 기본 채널 모델 함수
# ==============================================================================
def noise_power_dbm(bw_hz):
    """
    열잡음 전력 (dBm). [6]
        N = N0 + 10*log10(BW) + NF,   N0 = -174 dBm/Hz
    """
    return NOISE_FLOOR_DBM_PER_HZ + 10 * np.log10(bw_hz) + NOISE_FIGURE_DB


def path_loss_db(d_m, exponent):
    """
    Log-distance 경로 손실 모델. [1]

    Rappaport Eq.(3.93):  PL(d) = PL(d0) + 10*n*log10(d/d0) + Xσ
    본 코드는 섀도잉 항 Xσ를 생략하고 결정론적 부분만 사용한다.
    기준 거리 d0=1m 에서의 손실 PL(d0)은 Friis 자유공간 손실로 계산 [7]:
        PL(d0=1m) = 20*log10(f) - 147.55   (상수 147.55 = 20log10(4π/c))
    """
    d0 = 1.0
    pl_d0 = 20 * np.log10(d0) + 20 * np.log10(FREQ_HZ) - 147.55  # Friis 기준손실 [7]
    return pl_d0 + 10 * exponent * np.log10(d_m / d0)            # 거리 감쇠 [1]


# ==============================================================================
# 2. LoRa (단방향 링크) 수신 전력 & SNR
# ==============================================================================
def lora_rx_power_dbm(d_m):
    """
    LoRa 수신 전력 (dBm). 표준 링크 버짓 식. [1]
        Prx = Ptx + Gtx + Grx - PL(d)
    경로 손실 지수 = PATH_LOSS_EXPONENT (단방향이므로 1배)
    """
    pl = path_loss_db(d_m, PATH_LOSS_EXPONENT)  # 단방향 → 지수 그대로 [1]
    return (LORA_TX_PWR_DBM + LORA_TX_ANT_GAIN_DBI
            + LORA_RX_ANT_GAIN_DBI - pl)


def lora_snr_db(d_m):
    """LoRa SNR(dB) = Prx - Noise. [6]"""
    return lora_rx_power_dbm(d_m) - noise_power_dbm(LORA_BW_HZ)


# ==============================================================================
# 3. Backscatter (왕복 dyadic 링크) 수신 전력 & SNR
# ==============================================================================
def backscatter_rx_power_dbm(d_m):
    """
    Backscatter 수신 전력 (dBm). [2]

    핵심: reader -> tag -> reader 왕복(dyadic) 경로이므로
    경로 손실 지수가 단방향의 2배가 된다.
    Griffin & Durgin Eq.(2)의 모노스태틱 링크버짓은 분모에 (4πr)^4 를
    가지며, 논문은 "scattered power falls off as r^4"로 기술한다 -> 지수 2배.

    Prx = Pcarrier + 2*G_reader + 2*G_tag - PL_roundtrip - Loss
    여기서 monostatic(reader 송수신 겸함) 구조를 가정해
    PL_roundtrip = path_loss(2*exponent). 단, 논문 Eq.(2)의 변조계수 M,
    편파 X, 페이딩 마진 F2 등은 BACK_MODULATION_LOSS_DB로 통합·단순화함. [2]
    """
    # 왕복이므로 경로손실 지수를 2배로 [2]
    pl_roundtrip = path_loss_db(d_m, 2 * PATH_LOSS_EXPONENT)
    prx = (BACK_CARRIER_PWR_DBM
           + 2 * BACK_READER_GAIN_DBI   # 송신+수신 모두 reader 안테나
           + 2 * BACK_TAG_GAIN_DBI      # 입사+반사 모두 tag 안테나
           - pl_roundtrip
           - BACK_MODULATION_LOSS_DB)   # 변조/편파/페이딩 통합 손실 [2]
    return prx


def backscatter_snr_db(d_m):
    """Backscatter SNR(dB). [6]"""
    return backscatter_rx_power_dbm(d_m) - noise_power_dbm(BACK_BW_HZ)


# ==============================================================================
# 4. SNR -> BER 변환 (Coherent BPSK over AWGN)
# ==============================================================================
def ber_from_snr_db(snr_db):
    """
    BER = 0.5 * erfc( sqrt(SNR_linear) )   (Coherent BPSK over AWGN) [4]

    Proakis & Salehi Eq.(4.3-13):  Pb = Q( sqrt(2*Eb/N0) )
    Q함수-erfc 항등식 Q(x)=0.5*erfc(x/sqrt(2)) 를 적용하면
    Pb = 0.5*erfc( sqrt(Eb/N0) ) 이고, Eb/N0 = SNR 이므로 아래와 동일.
    """
    snr_lin = 10 ** (snr_db / 10.0)
    return 0.5 * erfc(np.sqrt(snr_lin))


# ==============================================================================
# 5. ALOHA 기반 네트워크 처리량 (다중 노드 경합) [5]
# ==============================================================================
def pure_aloha_throughput(offered_load_G):
    """
    Pure ALOHA 정규화 처리량.  S = G * exp(-2G)  [5]

    Abramson Eq.(2) 원전 표기는 rτ = Rτ * exp(-2Rτ) 이며,
    여기서 G ≡ Rτ(channel traffic), S ≡ rτ(channel utilization).
    이론상 최댓값은 G=0.5에서 S = 1/(2e) ≈ 0.184.
    (LoRaWAN MAC을 Aloha-like로 근사하는 통상적 모델링)
    """
    return offered_load_G * np.exp(-2 * offered_load_G)


# ==============================================================================
# 6. 시뮬레이션 실행 & 그래프 생성
# ==============================================================================
def run_and_plot():
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("LPWAN (LoRa) vs Backscatter  —  Comparison Simulation\n"
                 "(all equations sourced; see code docstrings)",
                 fontsize=14, fontweight='bold')

    # ---- (1) 거리 vs 수신 전력 ----------------------------------------------
    ax = axes[0, 0]
    distances = np.linspace(1, 2000, 500)  # 1m ~ 2km
    lora_prx = [lora_rx_power_dbm(d) for d in distances]
    back_prx = [backscatter_rx_power_dbm(d) for d in distances]

    ax.plot(distances, lora_prx, label="LoRa (one-way, α)", color="#1f77b4", lw=2)
    ax.plot(distances, back_prx, label="Backscatter (round-trip, 2α)",
            color="#d62728", lw=2)
    ax.axhline(LORA_SENSITIVITY_DBM, ls="--", color="#1f77b4", alpha=0.6,
               label=f"LoRa sensitivity ({LORA_SENSITIVITY_DBM} dBm)")
    ax.axhline(BACK_SENSITIVITY_DBM, ls="--", color="#d62728", alpha=0.6,
               label=f"Backscatter rx sens. ({BACK_SENSITIVITY_DBM} dBm)")
    ax.set_xlabel("Distance (m)")
    ax.set_ylabel("Received Power (dBm)")
    ax.set_title("(1) Received Power vs Distance\n"
                 "Backscatter decays ~2x faster [2]")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # ---- (2) 거리 vs BER ----------------------------------------------------
    ax = axes[0, 1]
    distances2 = np.linspace(1, 1500, 500)
    lora_ber = [ber_from_snr_db(lora_snr_db(d)) for d in distances2]
    back_ber = [ber_from_snr_db(backscatter_snr_db(d)) for d in distances2]

    ax.semilogy(distances2, lora_ber, label="LoRa", color="#1f77b4", lw=2)
    ax.semilogy(distances2, back_ber, label="Backscatter", color="#d62728", lw=2)
    ax.axhline(1e-3, ls="--", color="gray", alpha=0.6, label="BER = 1e-3 target")
    ax.set_xlabel("Distance (m)")
    ax.set_ylabel("Bit Error Rate")
    ax.set_title("(2) BER vs Distance (BPSK/AWGN) [4]")
    ax.set_ylim(1e-6, 1)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, which="both")

    # ---- (3) 통신 가능 최대 거리 비교 (막대) --------------------------------
    ax = axes[1, 0]

    def max_range(rx_func, sens_dbm):
        # 충분히 넓은 범위를 탐색해 상한에 걸리지 않도록 함
        ds = np.linspace(1, 100000, 200000)  # 1m ~ 100km
        prx = np.array([rx_func(d) for d in ds])
        ok = ds[prx >= sens_dbm]
        return ok.max() if len(ok) else 0.0

    lora_range = max_range(lora_rx_power_dbm, LORA_SENSITIVITY_DBM)
    back_range = max_range(backscatter_rx_power_dbm, BACK_SENSITIVITY_DBM)

    bars = ax.bar(["LoRa\n(LPWAN)", "Backscatter"],
                  [lora_range, back_range],
                  color=["#1f77b4", "#d62728"], alpha=0.85)
    ax.set_ylabel("Max Communication Range (m)")
    ax.set_title("(3) Max Range (until Prx = Sensitivity)")
    for b, v in zip(bars, [lora_range, back_range]):
        ax.text(b.get_x() + b.get_width()/2, v,
                f"{v:.0f} m", ha="center", va="bottom", fontweight="bold")
    ax.grid(True, alpha=0.3, axis="y")

    # ---- (4) 다중 노드 처리량 (ALOHA) --------------------------------------
    ax = axes[1, 1]
    G = np.linspace(0.01, 3, 300)  # offered load
    S = pure_aloha_throughput(G)

    ax.plot(G, S, color="#2ca02c", lw=2, label="Pure ALOHA  S=G·e^(-2G)")
    g_opt = 0.5
    ax.axvline(g_opt, ls="--", color="gray", alpha=0.6)
    ax.plot(g_opt, pure_aloha_throughput(g_opt), "o", color="red",
            label=f"Max ≈ {pure_aloha_throughput(g_opt):.3f} @ G=0.5")
    ax.set_xlabel("Offered Load  G  (∝ number of nodes × tx rate)")
    ax.set_ylabel("Normalized Throughput  S")
    ax.set_title("(4) MAC Throughput vs Load [5]\n"
                 "(LoRaWAN modeled as Aloha-like)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    out = "lpwan_vs_backscatter_results.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"[저장됨] {out}")

    # ---- 콘솔 요약 ----------------------------------------------------------
    print("\n" + "=" * 60)
    print("시뮬레이션 요약")
    print("=" * 60)
    print(f"LoRa  잡음전력      : {noise_power_dbm(LORA_BW_HZ):8.2f} dBm "
          f"(BW={LORA_BW_HZ/1e3:.0f} kHz)")
    print(f"Back  잡음전력      : {noise_power_dbm(BACK_BW_HZ):8.2f} dBm "
          f"(BW={BACK_BW_HZ/1e6:.0f} MHz)")
    print(f"LoRa  최대 통신거리 : {lora_range:8.0f} m")
    print(f"Back  최대 통신거리 : {back_range:8.0f} m")
    print(f"거리 비율 (LoRa/Back): {lora_range/max(back_range,1):8.1f} x")
    print("=" * 60)
    return out


if __name__ == "__main__":
    run_and_plot()
