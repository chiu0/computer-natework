# Low Power/Massive Networks

**Problem**
- The limitations of existing cloud-oriented IoT systems are four factors: High power use, Network congestion, Latency, and Rising cost.

**Solutions**
- In an era when IoT devices are exploding, the key question is simple. How can I connect more devices with less power? We researched three of the answer technologies: LPWAN, Backscatter, and Edge AI and TinyML, and the first two communication technologies went as far as simulating comparisons with direct code.

**Referenced Graphs**
<img width="1230" height="940" alt="image" src="https://github.com/user-attachments/assets/ff22219a-7973-42d0-a79c-e310f583270f" />
- Here are four graphs of results. The upper left is the received power over distance. The blue line is LoRa and the red line is Backscatter, and you can see the red line falling much steeper over distance, because of the round trip loss.
The upper right is the bit error rate by distance. The backscatter experiences a sharp rise in error rates over much shorter distances. The lower left is the bar comparison of the maximum communication distance, the lower right is the ALOHA throughput curve, which peaks at the point of load 0.5. Those are four key numbers. In this setting, LoRa's maximum communication distance is about 35,000 meters, and the backscatter is about 52 meters. That's almost 678 times the difference in percentage terms. And the ALOHA theory maximum throughput was 0.184.
Here's how it is interpreted. Because the round-trip path loss doubles, the received power of the backscatter attenuates approximately twice as fast as the distance. The result is that the communication distance is sharply divided into tens of meters versus tens of kilometers, which is the essential trade-off of the two technologies. For the same reason, the backscatter worsens over much shorter distances.
Finally, based on the ALOHA model, throughput is limited by up to 18.4% when multiple nodes compete. This is a common challenge for both technologies in large environments: LPWAN for distance and Backscatter for power.

**Proper Citations**
- [1] T. S. Rappaport, Wireless Communications: Principles and Practice, 2nd ed. Upper Saddle River,
NJ, USA: Prentice Hall, 2002, Sec. 3.11.3, Eq. (3.93).
[2] J. D. Griffin and G. D. Durgin, “Complete link budgets for backscatter-radio and RFID systems,” IE
EE Antennas Propag. Mag., vol. 51, no. 2, pp. 11–25, Apr. 2009.
[3] Semtech Corp., “SX1276/77/78/79 — 137 MHz to 1020 MHz Low Power Long Range Transceiver
,” Datasheet, Rev. 7, Camarillo, CA, USA, May 2020.
[4] J. G. Proakis and M. Salehi, Digital Communications, 5th ed. New York, NY, USA: McGraw-Hill, 20
08, Eq. (4.3-13).
[5] N. Abramson, “The ALOHA system: Another alternative for computer communications,” in Proc.
AFIPS Fall Joint Comput. Conf., vol. 37, 1970, pp. 281–285.
[6] C. Röhrig, D. Heß, and B. H. D. Trinh, “System design for distributed energy management using
multiple LPWAN technologies,” in Proc. IECON 2025 — 51st Annu. Conf. IEEE Ind. Electron. Soc., 2025.
[7] Recommendation ITU-R P.525-3, “Calculation of free-space attenuation,” ITU-R, Geneva, Switzer
land, Sep. 2016, Annex 1, Eq. (3).
[8] B. S. Chaudhari and M. Zennaro, Eds., LPWAN Technologies for IoT and M2M Applications. Camb
ridge, MA, USA: Academic Press, 2020.
[9] V. Liu, A. Parks, V. Talla, S. Gollakota, D. Wetherall, and J. R. Smith, “Ambient backscatter: Wirele
ss communication out of thin air,” in Proc. ACM SIGCOMM, 2013, pp. 39–50.
[10] V. Talla, M. Hessar, B. Kellogg, A. Najafi, J. R. Smith, and S. Gollakota, “LoRa backscatter: Enabli
ng the vision of ubiquitous connectivity,” Proc. ACM Interact. Mobile Wearable Ubiquitous Technol.
(IMWUT), vol. 1, no. 3, pp. 1–24, Sep. 2017.
[11] D. Darsena, G. Gelli, and F. Verde, “Modeling and performance analysis of wireless networks wi
th ambient backscatter devices,” IEEE Trans. Commun., vol. 65, no. 4, pp. 1797–1814, Apr. 2017.
[12] M. A. Jamshed, B. Haq, M. A. Mohsin, A. Nauman, and H. Yanikomeroglu, “Artificial intelligence
, ambient backscatter communication and non-terrestrial networks: A 6G commixture,” arXiv, 2023.
[13] P. Warden and D. Situnayake, TinyML: Machine Learning with TensorFlow Lite on Microcontroll
ers. Sebastopol, CA, USA: O’Reilly Media, 2019.
[14] C. Banbury et al., “Benchmarking TinyML systems: Challenges and directions,” arXiv:2003.0482
1, 2021.
[15] Google, “LiteRT for Microcontrollers (TensorFlow Lite for Microcontrollers),” 2024. [Online]. Av
ailable: https://ai.google.dev/edge/litert/microcontrollers/overview
- Numbers 1 through 7 are the sources on which the simulation was based — path loss followed by Rappaport, Backscatter link bugging followed Griffin and Durgin, LoRa reception sensitivity followed Semtech data sheets, bit error rates followed Proakis, ALOHA throughput followed by Abramson, and noise and transmission power numbers followed ITU-R and Röhrig.
Numbers 8 to 15 are the documents summarized in our group's data survey — LPWAN is Chaudhari and Zennaro, Backscatter is from Liu, Talla, and Gollakota researchers at the University of Washington, and network modeling studies by LoRa backscatter, Darsena, and Edge AI and TinyML are from Warden, Situnayake, Banbury, and Google.

**Logical Deductions**
- Premises:
Simulation results show that the power-efficiently maximized backscatter is only capable of short-range communication, and the distance-maximized LPWAN (silver active signal amplification) consumes a large amount of node power. When large nodes compete, under the Pure ALOHA mechanism, the maximum throughput is limited to 18.4% regardless of the communication scheme.
Deductions:
It is not possible to address the physical limitations of wireless transmission itself within the transmission layer. As a result, an architectural breakthrough is achieved only when raw data is first compressed and screened at the higher layer, the data processing layer, and the number of packets itself released over the air is physically reduced. Technology has a complementary dependency, not a substitute. When Edge AI hits the data volume, it can simultaneously achieve the two seemingly incompatible goals of low power and large scale by sending the remaining core packets to the backscatter or LPWAN depending on the power situation.

**Video Link**
- [youtube.com/watch?v=jF507OCnZ-k&source_ve_path=OTY3MTQ&embeds_widget_referrer=https%3A%2F%2Fmylms.korea.ac.kr%2F&embeds_referring_euri=https%3A%2F%2Fkucom.korea.ac.kr%2F&embeds_referring_origin=https%3A%2F%2Fkucom.korea.ac.kr](https://www.youtube.com/watch?v=jF507OCnZ-k&feature=youtu.be)

**code**
- https://github.com/chiu0/computer-natework/blob/main/lpwan_vs_backscatter.py
