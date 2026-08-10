---
status: oa_fulltext
paper_name: "基于机器学习的水体化学需氧量高光谱反演模型对比研究"
research_object: "水体化学需氧量(COD)"
original_paper_url: "Papers\\md\\A Comparative Study of the COD Hyperspectral Inversion Models in _Water Based on the Maching Learning.md"
resolved_doi: "10.7498/aps.73.20241022"
resolved_url: "https://doi.org/10.7498/aps.73.20241022"
oa_pdf: "https://wulixb.iphy.ac.cn/pdf-content/10.7498/aps.73.20241022.pdf"
preprocessing_method: "平滑(SG smoothing), 多元散射校正(MSC), 平滑结合MSC"
feature_extracting_method: "主成分分析(PCA)"
---

# 基于机器学习的水体化学需氧量高光谱反演模型对比研究

**Authors:** Gong Yi-Chun, Ming Jian-Yu, Siqi Wu, Ming-Dong Yi, Ling-Hai Xie, Wei Huang, Hai-Feng Ling

**Journal:** Acta Physica Sinica

**Year:** 2024

## Abstract

Memristors stand out as the most promising candidates for non-volatile memory and neuromorphic computing due to their unique properties. A crucial strategy for optimizing memristor performance lies in voltage modulation, which is essential for achieving ultra-low power consumption in the nanowatt range and ultra-low energy operation below the femtojoule level. This capability is pivotal in overcoming the power consumption barrier and addressing the computational bottlenecks anticipated in the post-Moore era. However, for brain-inspired computing architectures utilizing high-density integrated memristor arrays, key device stability parameters must be considered, including the on/off ratio, high-speed response, retention time, and durability. Achieving efficient and stable ion/electron transport under low electric fields to develop low-voltage, high-performance memristors operating below 1 V is critical for advancing energy-efficient neuromorphic computing systems. This review provides a comprehensive overview of recent advancements in low-voltage memristors for neuromorphic computing. Firstly, it elucidates the mechanisms that control the operation of low-voltage memristor, such as electrochemical metallization and anion migration. These mechanisms play a pivotal role in determining the overall performance and reliability of memristors under low-voltage conditions. Secondly, the review then systematically examines the advantages of various material systems employed in low-voltage memristors, including transition metal oxides, two-dimensional materials, and organic materials. Each material system has distinct benefits, such as low ion activation energy, and appropriate defect density, which are critical for optimizing memristor performance at low operating voltages. Thirdly, the review consolidates the strategies for implementing low-voltage memristors through advanced materials engineering, doping engineering, and interface engineering. Moreover, the potential applications of low-voltage memristors in neuromorphic function simulation and neuromorphic computing are discussed. Finally, the current problems of low-voltage memristors are discussed, especially the stability issues and limited application scenarios. Future research directions are proposed, focusing on exploring new material systems and physical mechanisms that could be integrated into device design to achieve higher-performance low-voltage memristors.

## Content

 
综述
面向类脑计算的低电压忆阻器研究进展*
贡以纯#    明建宇#    吴思齐    仪明东    解令海    黄维    凌海峰†
(南京邮电大学材料科学与工程学院, 有机电子与信息显示国家重点实验室, 南京　210023)
(2024 年7 月23日收到; 2024 年8 月30日收到修改稿)
忆阻器是非易失性存储器和神经形态计算的优秀候选者. 电压调制作为其关键性能策略, 是获得纳瓦超
低功耗、飞焦超低能耗工作的基础, 有助于打破功耗墙、突破后摩尔时代算力瓶颈. 然而基于高密度集成忆
阻器阵列的类脑计算架构还需重点考虑开/关比、高速响应、保留时间和耐久性等器件稳定性参数. 因此如何
在低电场下实现离子/电子的高效、稳定驱动, 构筑电压低于1 V的低电压、高性能忆阻器成为了当前实现类
脑计算能效系统的关键问题. 本文综述了近年来面向类脑计算的低电压忆阻器的研究进展. 首先, 探讨了低
电压忆阻器的机制, 包括电化学金属化机制和价态变化机制. 在此基础上, 系统总结了各材料体系在低电压
忆阻器中的优势, 涵盖了过渡金属氧化物、二维材料和有机材料等. 进一步围绕材料工程、掺杂工程、界面工
程提出了相应的低电压忆阻器实现策略, 最后, 展望了基于低电压忆阻器的类脑功能模拟及神经形态计算应
用, 并对现存问题和未来研究方向进行了讨论.
关键词：忆阻器, 低电压, 类脑计算
PACS ：73.40.Rw, 81.07.–b, 85.35.–p, 07.05.Mh 　DOI:  10.7498/aps.73.20241022
CSTR ：32037.14.aps.73.20241022
 
1   引　言
随 着 人 工 智 能 和 物 联网 (internet  of  things,
IoT)的发展, 来自数据中心和边缘设备的数据量
急剧增加, 高密度非易失性存储技术是大数据时代
实现海量信息计算的关键技术. 然而接近极限的物
理微缩尺寸比例和传统冯·诺伊曼计算架构使得算
力提升变得愈发困难, 发展基于新原理电子元件的
类脑计算范式对进入后摩尔时代至关重要[1]. 其中
忆阻器作为新原理电子元件中最有代表性的无源
器件, 内部阻值由历史操作所决定. 在撤去供电后,
内部阻值在无复位操作下可在长时间尺度内保持
不变, 呈现非易失性[2]. 与传统CMOS存储器相比,
这种历史依赖的时间信息整合能力赋予了忆阻器
类脑工作机制, 以此构筑了人工突触[3]、神经元[4]、胞
体[5]等一系列神经形态硬件[6]. 同时基于高速、高
密度、低功耗的忆阻器交叉阵列天然构建的矩阵向
量, 可以通过基尔霍夫定律与欧姆定律原位执行高
并行乘加计算过程. 这种类脑计算范式已被应用于
诸如机器学习[7,8]、图像处理[9–12]等数据密集型任务
的硬件加速器, 展示出了显著的算力和能效优势.
为了执行高能效的计算任务, 低硬件开销的大
规模忆阻器阵列是必需的. 其中, 忆阻器的低功
耗工作特性是降低器件噪声水平、阻态漂移、热
效应等非理想因素的关键[6,13]. 根据功耗计算方式
(功耗=电压×电流), 降低运行电压(≤1 V)和电
流(~nA)是获得纳瓦超低功耗、近飞焦超低能耗
 
*  国家重点研发计划(批准号: 2021YFA0717900)、国家自然科学基金(批准号: 62288102, 22275098, 62471251)和江苏省研究生科
研与实践创新计划项目(批准号: 46030CX21252)资助的课题.
#  同等贡献作者.
†  通信作者. E-mail: iamhfling@njupt.edu.cn
©  2024 中国物理学会  Chinese Physical Society http://wulixb.iphy.ac.cn
物 理 学 报   Acta  Phys.  Sin .   Vol.  73, No.  20 (2024 )    207302 
207302-1

工作的基础, 是打破后摩尔时代限制芯片算力提升
功耗墙的主要渠道之一[14–16]. 忆阻器的工作原理
通常涉及电场驱动下材料内部的离子通量变化(例
如离子迁移或氧空位的移动), 使得内部电流和电
压之间存在非线性关系, 其阻值状态由特定电压下
的电流决定. 忆阻器完成阻态切换过程中将产生显
著的电流响应, 降低电流水平可能难以兼顾维持时
间、开关比、循环耐久性等器件性能稳定性参数[17–19].
如何在低电场下实现离子的高效、稳定驱动, 进而
构筑电压低于1 V的低电压、高性能忆阻器成为了
当前实现类脑计算能效系统的关键问题. 为了实现
这一目标, 研究者们正致力于开发新的材料体系和
结构设计, 以提高忆阻器在低电压下的离子迁移效
率. 例如, 通过界面工程和纳米结构调控, 可以从
离子迁移能量角度优化传输过程, 从而实现低功耗
高效能的忆阻器. 此外, 低电压条件下稳定的脉冲
传递和突触权重调制有望在全面降低系统的能量
消耗的同时保证计算精度. 低电压操作不仅延长了
器件的使用寿命, 提高了系统的可靠性, 还使大规
模神经网络的低硬件开销成为可能, 满足了类脑计
算对低功耗和的高能效双重要求, 从而为未来的类
脑计算系统提供坚实的硬件基础.
本综述旨在全面回顾面向类脑计算的低电压
忆阻器机制、材料和低电压忆阻器实现策略, 并探
讨基于低电压忆阻器的功能应用, 文章整体结构如
图1所示. 本文首先根据开关机制和材料的不同对
主流忆阻器进行分类, 并对针对其特性进行具体讨
论与分析. 然后总结了实现低电压忆阻器的策略,
通过这些策略可以有效降低忆阻器的工作电压, 并
兼具性能、功能稳定性, 同时将代表性低电压器件
参数在表1中进行汇总. 最后调研了低电压忆阻器
的功能应用, 并总结了其未来的发展与挑战. 
2   面向类脑计算的低电压忆阻器机制 
2.1    电化学金属化机制
基 于 金 属 阳 离 子 迁 移 的 电 化 学 金 属 化 机制
(electrochemical metallization, ECM)是忆阻器中
 
典型材料                       功
能
应
用
                                                               工
作
机
制
金属氧化物 有机材料
金属卤化物
二维材料
调制策略
< 1 V
低电压忆阻器
高效、稳定传输 神经元/突触模拟
电化学金属化 (细丝型)
价态变化
(细丝型/界面型)
掺杂工程
Top electrode
Bottom electrode
Top electrode
Bottom electrode
Top electrode
Bottom electrode
Top electrode
Bottom electrode
掺杂工程
界面工程
+
LRS
+
LRS
+
Set
-
Reset
生物接口
神经网络
…
…
ST1
Input
layer
2
Output
layer
3
10 8
Hidden layer
Neuron spik
ST2
 
图 1    综述框架示意图[20–27]
Fig. 1. Schematic of the overview framework[20–27].
物 理 学 报   Acta  Phys.  Sin .   Vol.  73, No.  20 (2024 )    207302 
207302-2

 
表 1    低电压忆阻器性能总结
Table 1.    Summary of low-voltage memristor performance.
器件
结构 工作机制 开关电压 开关比 开关
速度/ns
保留
时间
耐久性
(循环)
功耗/
能耗 应用 文献
Pt/HfAlOx/TaN VCM BRS:
+1/–1 V — 50 — — 4.28 aJ 手写数字识别 [171]
Ta/Ta2O5:Ag/Ru ECM BRS:
+0.7 V/–0.7 V — 100 ≈5×104 s 5×107 — — [42]
Pt/YSZ/Zr VCM BRS:
+0.7 V/–0.7 V — 2 104 s 108 — — [172]
Ag/SnOx/SnSe ECM BRS: +0.4/–0.1 V >103 — 105 s 4000 — — [157]
EGaIn/MACsPbI/
PEDOT: PSS/ITO VCM BRS:
+0.6/–0.41 V >105 — 105 s 104 3.8 mW — [114]
ITO/FA1–yMAyPbI3–xClx/
(PEA)2PbI4/Au VCM BRS:
+1.0/–0.5 V — — — 200 1 fJ 突触功能模拟 [49]
Ag/PMMA/MAPbI3:
Ag/Au ECM TS:±0.22 V — 40 — 2500 10 μW 伤害传感器 [59]
Ag/CsPbI3/Ag ECM TS:100 mV — — 100 ms — 2 nW 储备池计算 [111]
PET-ITO/MAPbI3/
PEAI/Au VCM BRS:
+1/–1 V — — — 50 13.5 aJ 神经元积分-
发放功能 [152]
Ag/MoOx/
CsI (CsBr)/Ag ECM BRS:
–0.16/+0.07 V >1010 <200 >106 s >105 <3.31 pW 模拟手写数字
分类 [62]
Pt/CuI/Cu ECM BRS:
+0.64/–0.19 V 103 — 17 h 125 8.73 µW 图像硬件加密
和解密 [10]
Ag/PMMA/
Cs2AgBiBr6/ITO ECM BRS:
+0.6/–0.6 V >10 — — — 188 pJ 手写数字识别 [58]
Pt/MoS2/Ti VCM BRS:
+0.65/–0.90 V 160 — 10 years 1×107 — — [117]
Au/HfSe2/Au VCM BRS:
+0.742/–0.817 V 102 — — 500 0.82 pJ 矩阵计算 [80]
Ag/BNOx/Graphene ECM BRS: 0.6/0.1 V 100-1000 — — 100 — — [75]
Ag/Protein nanowires/Ag ECM TS:60 ± 4 mV — — — 104 — 神经元-突触
联立积分发放 [126]
Au/PBFCL10/Ag ECM BRS:
+0.2/–0.2 V — 21 >106 s — 2.35 μW HNN [131]
ITO/PEDOT:PSS/
pTPD/CsPbBr3NCs/Ag ECM TS:<1 V 103 — 105 s
TS:2×106
BRS:5.6×
103
— 储备池计算 [154]
Au/MSFP/Au VCM BRS:
+1.0/–1.0 V — — 104 s 100 — 图像处理 [106]
ITO/PVK:TCNQ/Ag ECM
BRS:
+0.69/–0.52 V
TS:0.21 V
≈103 — 104 s 104 15.2 μW 突触、神经元
功能模拟 [109]
Au/TPPS/Au VCM BRS:
–0.1/+0.3 V — — — —
16.25 pW
—
2.06 nW
突触模拟 [105]
W(Ag)/PI/Pt/Ti ECM TS:0.56 V ≈103 — 0.44 ms 300 80 nW 图像处理 [107]
Pt/CuZnS/Ag ECM Vset=0.089 V ≈106 — >1000 s 100 0.1 nW 模式识别 [132]
Pt/DDP-CuNPs/Au VCM TS:4 mV — — — 100 — SNN [145]
Ag/c-YY NW/Ag ECM TS:≤0.1 V 106 — — — 750 fJ SNN [124]
Ag/Ag-IPS/Au ECM BRS:
+0.43/–0.21 V 108 100 105 s 900 18.5 fJ 图像处理 [138]
Ag/PMMA/MAPbI3:
Ag/Au ECM TS:≈0.2 V — 40 — 2500 — 伤害感受器 [59]
Al/Ti3C2:Ag/Pt VCM BRS:
+2.0/–2.0 V — — — 106 0.35 pJ 突触模拟 [137]
Ag/TiO2:Ag/Pt ECM BRS:
+0.1/–0.1 V — — — — 26.0 pJ 突触模拟 [140]
ITO/NiSAs/
N-C/PVP/Au VCM BRS:
+0.7/–1.1 V 103 100 >106 s 500 — 全加器 [99]
Au/silk: AgNO3/Ag ECM TS:0.17 V 3 × 106 — 103 s 100 — 突触模拟 [147]
Ag/MXene/Pt ECM BRS:
+1.33/–0.94 V >105 — 104 s 103 1~10 fJ ANN [149]
物 理 学 报   Acta  Phys.  Sin .   Vol.  73, No.  20 (2024 )    207302 
207302-3

的典型机制之一. 1976年, Hirose和Hirose[20]首
次报道了基于阳离子迁移的阻变行为, 并分别于
1998和2010年被进一步应用于存储和神经形态
计算研究[28]. 基于ECM的器件的电阻变化是通过
施加电压, 在固态阻变介质中产生金属离子的迁移
和还原, 形成导电细丝. 反向电压可以使这些金属
离子重新氧化并回到阻变介质中, 断开导电细丝
(conductive  filament,  CF).  整 体 过 程 包 括 活 性 
金属电极的氧化注入、迁移、还原形成连续的金属
导电通道(如图2(a)所示). 为了稳定实现ECM过
程, 具备适宜吉布斯标准自由能(standard Gibbs
free  energy,  ∆G°)的 金 属 阳 极 (如 Ag,  Ni和 Cu)
是必不可少的, 阴极通常选择惰性金属(如Au, Pt,
W和Ir). 得益于快速氧化还原的金属导电通道的
软击穿过程, 基于ECM的忆阻器通常具有很高的
开关速度, 可以在纳秒到微秒级的时间内完成状态
转换. 这使得它们在需要快速阻值切换的应用中
(如时序信号采集、脉冲神经网络)具备低功耗优
势. 同时, 金属阳离子的运动主要受外部电场和离
子浓度梯度的影响, 因此预先掺杂的金属离子、周
表 1 （续）　低电压忆阻器性能总结
Table 1 (continued).　Summary of low-voltage memristor performance.
器件
结构 工作机制 开关电压 开关比 开关
速度/ns
保留
时间
耐久性
(循环)
功耗/
能耗 应用 文献
Ag/a-COx/ta-C/Pt ECM BRS:1.5 V/–1.0 V — — 100 s — 6 nW — [155]
Au/h-BN/Au VCM TS:0.1 V 107 40 >20000 s 500 — 逻辑门 [158]
Ag/GeTe/MoTe2/Pt ECM BRS:
+0.15/–0.14 V 102 — 104 s 105 ≈30 nJ 突触模拟 [162]
Ag/SnS/Pt ECM BRS:
+0.2/–0.1 V 108 1.5 105 s 104 100 fJ 图像分类 [73]
 
ECM
(b)
(c)
(a)
(d)






(e) (f)
Initial state +
Forming
Initial state +
LRS
+
Set
-
Reset
Initial state +
LRS
VCM
 
图 2    两种典型的忆阻器开关机制　(a) ECM示意图; (b) VCM细丝型示意图; (c) 界面型示意图; (d)双极型开关的典型电流-
电压(I-V)特性曲线; (e) 阈值型开关的I-V特性曲线; (f) 模拟类开关的I-V特性曲线
Fig. 2. Two typical switching mechanisms of memristors: (a) Schematic diagram of ECM; (b) schematic diagram of filamentary-type
VCM; (c) schematic diagram of interfacial-type VCM; (d) typical I-V characteristics of bipolar resistive switching; (e) typical I-V
characteristics of threshold switching; (f) typical I-V characteristics of analog switching.
物 理 学 报   Acta  Phys.  Sin .   Vol.  73, No.  20 (2024 )    207302 
207302-4

围环境的湿度(质子)也对金属离子的电化学氧化
还原过程具有重要影响. 这归因于电极和固体阻变
介质界面处的电化学半电池反应(能斯特电位)对
扩散电位的调节, 为低电场驱动金属离子提供了可
能性[29]. 
2.2    价态变化机制
忆阻器的另一种主要工作机制是基于阴离子
迁移的价态变化机制(valence change mechanism,
VCM). VCM主要是在外部条件下(例如电场、光
或温度)驱使阴离子在材料内部完成重新分布, 并
最终导致材料电阻的变化. 典型的阴离子是氧、硫
和硒化物离子, 在有机材料体系中还使用有机阴离
子(如铵根离子、乙酸根离子等)[30]. 在近年报道中,
卤素或硫属阴离子逐渐被用于低电压忆阻器的研
究[31,32].
如图2(b)所示, 一般而言, 氧离子或等效的带
正电荷的氧空位(Vos)比其他组分更容易运动, 通
常被认为在阻变中扮演载流子的角色. 原则上Vos
的迁移主要由电场或热效应诱导, 形成连续的带电
通道将会导致整体电导率的改变[21]. 当对顶电极
施加正偏压, 受电场驱动的氧离子会向顶电极移动
形成富氧区, 并在阻变介质中形成氧浓度梯度, 其
中离子的迁移和再分布会导致材料的局部化学状
态变化, 进而影响电导状态. 在复位过程中, 氧离
子从阴极迁移到导电丝尖端, 导致导电丝的长度减
小产生间隙区域, 使得器件回到高阻态.
为了实现电导连续可调的阻变过程, 离子在阻
变介质与金属电极界面处均匀迁移的“界面型”的
机制得到了广泛关注[33]. 这种多态模拟特性对于
高效的类脑计算和存储器件具有重要意义, 能够在
低功耗条件下实现高密度的信息存储和处理[34,35].
如图2(c)所示, 相较于纯粹的CF型阻变, 界面型
阻变是一种均匀传导机制, 由场诱导的肖特基结的
变化所控制, 器件的电导率和器件面积成正比. 这
种界面型阻变可以在较低的操作电压下实现稳定
且连续的阻变过程, 减少了因高电场和高温引起的
器件退化和性能不稳定问题. 此外, 界面型和CF
型阻变通常共存于同一个器件, 通过界面型和CF
型阻变的协同作用, 可以在不同的操作电压范围内
实现多态电导调节. 低电压下, 界面型阻变机制主
导, 表现为均匀的电导变化; 而在较高电压下, CF
型阻变机制可能被激活, 形成局部导电通道, 导致
显著的电导变化[36]. 
3   面向类脑计算的低电压忆阻器材料 
3.1    过渡金属氧化物
过 渡 金 属 氧 化物 (transition-metal-oxide,  TMO)
因其庞大的材料体系和CMOS工艺兼容性而成为
忆阻器的主流材料. 大部分介电材料因为缺乏天然
缺陷而只能在外加电场下完成硬击穿过程而非可
重复的软击穿过程, 因此在TMO基忆阻器研究
中(如TiO2, HfO2 (如图3(a)所示)等)主要依靠
多晶态氧化物薄膜中的晶格缺陷产生以氧空位迁
移形成的CF, 表现出以双极型切换(bipolar resis-
tive switching, BRS)或阈值切换(threshold swith-
cing, TS)的数字类开关为主的阻变行为(见图2(d),
 
(a)
Hf
Mo S
B N
CO
O3
-S O 3
-S HO3S HO 3S HO 3S HO 3S
atct
O O O
O O O O O O
O O
S S S S S 

S
N Metal
O
Cation (Ti4+,
Zr4+, Mn4+ l)
Anion
Cation (Ca2+,
Cs+, La3+ l) Anion (S2-, Se2-, Te2- l)
Cation (Zn2+, Cd2+, Fe2+ l)
(d)
(b) (c) (f)
(e)
(g)
过渡
金属氧化物
金属
卤化物
二维
材料
有机
材料
 
图 3    (a) HfO2晶胞示意图; (b) 钙钛矿通式晶胞示意图; (c) 闪锌矿晶胞示意图; (d) MoS2层状结构示意图; (e) h-BN结构示意
图; (f) PEDOT:PSS分子示意图; (g) MTPP分子示意图
Fig. 3. (a) Schematic diagram of HfO2 unit cell; (b) schematic diagram of perovskite unit cell; (c) schematic diagram of sphalerite;
(d) schematic diagram of MoS2 layered structure; (e) schematic diagram of h-BN structure; (f) schematic diagram of PEDOT:PSS
molecule; (g) schematic diagram of MTPP molecule.
物 理 学 报   Acta  Phys.  Sin .   Vol.  73, No.  20 (2024 )    207302 
207302-5

(e)). 已报道了缺氧-富氧、掺杂-去掺杂等物理模型
可用于解释器件内部氧动力学过程[22]. 随着神经
形态计算的进一步发展, 具有非化学计量比的金属氧
化物可以更好地完成多态模拟电导调制(如图2(f)),
如HfOx[37],  AlOx[38–40],  TaOx[41,42],  NiO[43],  TiOx[44]
等金属氧化物在外加电场下的自掺杂过程, 这来源
自内部氧离子在外加电场下的定向移动所产生的
氧浓度梯度. 在低电压操作中, 面临着氧离子迁移
速度较慢、导电通道形成不均匀等问题. 可以通过
调控氧化物层的厚度和氧含量分布, 或引入界面修
饰技术提高氧离子的迁移效率和稳定性. 工作主要
集中于利用非化学计量比氧化物中非均匀的氧缺
陷分布或异质搭配具备氧含量差异的氧化物层, 使
得在低外场下更容易稳定产生氧离子/氧空位的定
向迁移过程[37].
此外, 基于电子-电子相互作用引起的金属-绝
缘体转变现象(Mott转变)相变材料也为低电压
驱动提供了基础. 在Mott材料中, 电子间的库仑
相互作用导致了电子局域化, 从而阻止了电荷传
输, 使得材料表现出绝缘特性. 当外部条件(如温
度、压力或电场)改变时, 这些局域化的电子可以解
除限制而运动, 导致材料快速从绝缘状态转变为金
属状态. 因此, 基于Mott转变的内在机制使得VOx
和NbOx基Mott忆阻器在低电场条件下仍能有效
工作, 具有低功耗、高速切换、高循环稳定性等优
势, 近年来成为低功耗振荡神经元、高速神经元、
脉冲神经网络(SNN)等研究中的理想选择[45–47]. 
3.2    金属卤化物材料
金属卤化物中的代表性材料是卤化物钙钛矿
(halide perovskite, HP)材料, 钙钛矿的通用化学
式为ABX3, 其中A和B为阳离子, X为与B八面
体配位的阴离子, 如图3(b)所示. 卤化物钙钛矿天
然耦合离子和电子电荷的特性, 可用于创建基于器
件内部动力学的高能效自适应计算系统[23]. 近年
来, 具有灵活原子间键合的HP被认为是低功耗神
经形态电子器件的合适材料, 如有机-无机铅卤化
物钙钛矿[48–50]、全无机卤化物钙钛矿[51–54]、无铅卤
化物钙钛矿和卤化物双钙钛矿等[55,56]. 基于HP的
忆阻器普遍由卤素空位或活性金属离子的迁移完
成工作过程, 因此降低薄膜缺陷以提升多种载流子
在HP中的迁移效率是实现低电压忆阻器的关键.
Ren等[57]制备了结构为Au/3-己基取代聚噻吩(poly
(3-hexylthiophene-2,  5-diyl),  P3HT)/CsPbBr2I/
ITO的钙钛矿忆阻器, 在0.5 V的工作电压下实现
了突触塑性调控, 搭配双层脉冲神经网络实现了机
器视觉应用. Lao等[58]制备了一种无铅、空气稳定
的Ag/聚甲基丙烯酸甲酯(poly-methylmethacry-
late, PMMA)/Cs2AgBiBr6/ITO器件, 可在±0.5 V
下完成阻变开关(resistive switching, RS)过程, 单
次突触事件功耗仅为188 pJ. 由于HP中离子运动
的活化能低, 可在超低电压下实现快速可调的离子
迁移, Jang等[59]基于Ag/PMMA/MAPbI3:Ag/Ag
的扩散型忆阻器(diffusive memristor)实现了低
于0.2 V的阈值开关过程. CF稳定性由细丝与阻
变介质之间的接触状况决定, 而金属原子流动趋向
于最小化表面能, 使得细丝表面的性质动态变化不
可避免[60]. 快速的表面流动导致CF寿命缩短, 进
而赋予忆阻器扩散特性. 具有高表面扩散系数的
HP有利于控制导电细丝的易失性.
除了钙钛矿, 闪锌矿也是金属卤化物材料中被
广泛使用的一类(如图3(c)所示). Mishra等[61]报
道 了 基于 CuI的 阻 变 随 机 存 取 存 储 器 (resistive
random  access  memory,  RRAM),  实 现 了 小 于 
±0.5 V的低电压RS过程, 具有出色的耐久性(103
循环), 5×104 s的维持特性和104的稳定开/关比.
Su等 [62]用 Ag/MoOx/CsI/Ag结 构 获 得 了 超 过 
1010开/关比的可重构忆阻器, 表现超低且均匀的
工作电压(<0.18 V), 实现了在模拟手写数字分类
任务的高分类精度(>90%). 由于宽带隙的绝缘性
质, 卤化铯基阻变介质的忆阻器可以降低功耗并进
一步扩展动态范围. 
3.3    二维材料
如图3(d), (e)所示, 二维材料是通过平面内
强化学键和相对较弱的非平面范德瓦耳斯相互作
用(van der Waals, vdW)集成的材料类别, 包括
石 墨 烯、 过 渡 金 属 二 硫 族 化 物 (transition  metal
dichalcogenides, TMDs)[63,64]和六方氮化硼(hexag-
onal boron nitride, h-BN)[65–68]等. 由于其原子级
厚度、低电子态密度、高质量晶体结构、缺陷灵活
可调等特性, 使得基于二维范德瓦耳斯材料的忆阻
器件展现出超低电压、电流[69–74]、高均匀性[75]和
机械灵活性[76–78]. 此外由于二维范德瓦耳斯材料
的天然表面缺陷(如空位、晶界缺陷等)在界面处
会显著影响电子和离子的分布和传输, 使得其会与
物 理 学 报   Acta  Phys.  Sin .   Vol.  73, No.  20 (2024 )    207302 
207302-6

电极之间存在较强的界面作用, 因此选择适宜电极
制备方式和二维材料层间界面调控可以实现二维
材料忆阻器的稳定阻变, 通常基于缺陷工程的ECM
是其主流忆阻机制[24,79,80].
Feng等[81]通过开发一种低温气溶胶喷射印
刷技术, 展示了一个完全气溶胶喷射印刷Ag/MoS2/
Ag垂直忆阻器, 其中, Ag+在印刷的MoS2薄片的
垂直和横向间隙中扩散, 在0.18 V的低电压驱动
下, Ag+能够快速渗透并形成金属导电丝. Shi等[82]
利用化学气相沉积生长的多层h-BN片作为功能
层制备了基于金属/h-BN/金属的VCM忆阻器.
由于h-BN叠层中的硼空位的活化能较低, 从而大
大降低了开关所需的电压, 实现了约0.1 fW的开
关功耗. 相比于非晶态材料, 单晶材料具备规则而
密集的原子排列. Ding等[83]基于Ag+在单晶h-BN
层间的高迁移能垒(12.051 eV), 在垂直方向上限
制了金属细丝从二维到三维的形成过程, 降低了随
机生成概率, 提升了阵列的整体均匀性. 此外, 得
益于B, N, C不同的电子云密度, 单层六方氮化硼
原子可以在六角环的中心形成渗透孔道, 实现对质
子的低能耗快速传输过程[84]. 二维过渡金属碳化
物和氮化物(2D-MXene)由于其高导电率、高亲水
性等特点广泛应用至忆阻器领域[85,86]. Yan等[87]
利用片状二维Ti3C2Tx中Ti及O空位的生成, 完
成了10 ns脉宽脉冲下的超快响应过程. 由于氧离
子迁移率高、扩散势垒低, 对二维材料进行部分氧
化或进行氧化层异质堆叠可以改善阻变过程的稳
定性[88,89]. Wang等[90]设计了一种基于Ag/MoS2/
HfAlOx/碳纳米管(carbon nanotube, CNT)的可
重构忆阻器, 利用MoS2/HfAlOx在柔性纤维银电
极上高度均匀分布, 使得银离子可以完成快速均匀
的注入过程. 通过限流控制金属细丝生成的强弱程
度, 实现易失性和非易失性状态可重构切换, 完成
了低至1.9 fJ的神经元积分发放过程. Ahmed等[91]
利用Ag/BP/ITO结构中黑磷(black phosphorus,
BP)的自然局部氧化设计了具备快速氧离子及银
离子扩散能力的阻变存储器, 可以在0.39/–0.37 V
下保持大于107开关比及104循环次数. 
3.4    有机材料
相比于无机物(如氧化物)能带结构主导的电
子、离子特性, 在分子水平上设计的有机材料具备
更强的功能可调性, 尤其是在柔性与生物兼容性方
面, 这使得有机材料在神经形态可穿戴电子方面具
有更大的发展潜力[25,92]. 目前, 常用于忆阻器的有
机材料包括生物蛋白[93]、聚合物材料如聚3, 4-乙烯
二氧噻吩/聚苯乙烯磺酸盐(poly(3, 4-ethylenediox-
ythiophene)(styrenesulfonate)、PEDOT:PSS[94–96])
(如图3(f))、PMMA[97,98]、聚乙烯吡咯烷酮(polyv-
inyl pyrrolidone, PVP)[99,100]等, 有机框架材料如金
属卟啉(metalloporphyrin, MTPP)[101](如图3(g))、
金 属 酞菁 (metal  phthalocyanine,  Me-Pc)[102].  在
有机忆阻器中, 阻值切换过程主要依赖于电化学掺
杂或无电铸过程的电荷捕获[103,104].
Liu等[105]合成了一种质子贮库型4, 4′, 4′′, 4′′′-
(卟啉–5, 10, 15, 20-四基)四(苯磺酸)(TPPS)分
子, 制备了结构为Au/TPPS/Au的有机质子忆阻
器. 通过有序的质子迁移和界面自协同掺杂的发
生, 新的能级被引入分子带隙中, 从而有效地调节
器件的64个非易失电导态(>1800 s), 其单比特电导
调制的功耗处于16.25 pW—2.06 nW的较低水平.
Zhou等[106]首次展示了一种新兴的基于多峰修饰
丝 素 蛋白 (modified  silk  fibroin  protein,  MSFP)
的全硬件忆阻器视觉系统. 多级模拟电导能力主要
取决于MSFP薄膜中Li+掺杂浓度. 合适的残余Li+
浓度可以在MSFP功能膜中引入缺陷能级, 提供
合适的陷阱位点来存储注入的电子. Wang等[107]
在W/Ag/聚 酰 亚 胺 (polyimide,  PI)/Pt/Ti结 构 
下 实 现 了 低于 1 V的 TS过 程 ,  亚 阈 值 摆 幅 为
2.1 mV/dec. 由于PI中大量的含氟五元杂环和芳
香环提供了强大的分子间作用力, 芳香杂环的共轭
效应提供了很高的热稳定性和力学性能, 可以在恶
劣环境中稳定工作. Oh等[108]提出的基于聚1, 3,
5-三甲基–1, 3, 5-三乙烯基环三硅氧烷(p(V3D3-
co-VI)的突触忆阻器表现出基于Cu纳米簇的不
连续CF. 即使在低电压(<1 V)下, 这些忆阻器也
可以具有较大开关比(>104)的非易失性可控导电
细丝. 通过引入咪唑官能团来形成基于Cu纳米簇
的CF, 咪唑官能团为Cu纳米簇提供了成核位点.
Zhang等[109]利用Ag和7, 7, 8, 8-四氰基苯醌二
甲烷 (7,  7,  8,  8-tetracyanoquinodimethane,
TCNQ)之间的氧化还原配位反应, 基于Ag/PVK:
TCNQ/ITO结 构 实 现 了 低 的 工 作 电 压 (+0.55/
–0.21 V)和低功耗(2.07×10–5 W), 且开关比保持
在103. Wang等[110]报道了基于四(4-羧基苯基)
卟啉锌(zinc-tetrakis(4-carboxyphenyl)porphyrin,
物 理 学 报   Acta  Phys.  Sin .   Vol.  73, No.  20 (2024 )    207302 
207302-7

ZnTCPP)的超低的工作电压(≈80 mV)和功耗
(0.39 nW)的柔性忆阻器, 模拟了在连续可调的超
低电压脉冲(50 mV)下典型的突触可塑性, 进而
模拟机械刺激(100 mV)下的学习-遗忘-再学习特
性. 系统对手势的识别率高达97%, 并且在5 mm
弯曲状态的影响下仍保持在较高水平(91%). 
4   低电压忆阻器实现策略 
4.1    基于材料本征特性的低电压实现策略
忆阻器中的离子传输通常是在固体电解质或
离子导体中进行. 当施加电压时, 材料内部会产生
电场, 这个电场会作用于固体电解质中的离子使之
迁移, 离子的迁移难易程度由离子活化能/迁移势
垒进行评估. 一般来说, 活化能/迁移势垒越高, 离
子传输时所需的电压就越大. 因此本节主要关注材
料本征特性的优化和结构设计, 如通过纳米结构、
薄膜工艺、化学修饰等方法直接降低离子活化能/
迁移势垒, 减小离子传输所需的电压. 
4.1.1    本征缺陷优化离子传输
本征缺陷(intrinsic defects)是指材料结构中
自发产生的缺陷, 而非外界因素引入的. 它们通常
在材料的形成或生长过程中自发产生, 反映了材料
的固有特性. 通过采用具备天然缺陷位点和适宜缺
陷浓度的材料可以降低离子在材料中的活化能或
迁移势垒(如图4(a)). Lu等[73]制备了Ag/SnS/Pt
忆阻器, 实现了运行电压0.2 V、开关速度1.5 ns
 
(a) Top electrode
Bottom electrode
 Sn vacancy Ag Sn S



(b)
Voltage/V
Current/A
-0.2
10-4
10-6
10-8
10-10
10-12
0.2 0.4 0
(c)
 (d)
0.9
d/d/arb. units
0.6
0.3
-0.9
-0.3 0.3
Sample bias/V
0
Pristine SnS
Sn vacancy site
(e)
3.6 4.0 4.4
I La
I Lb1
I Lb2 I Lg1
4.8
Energy/keV
As fabricated
After SET
Normalized counts
(h)
0 50 100
Voltage/V
10-8
10-11
10-14
Current/A
(g)
(f) Ag AgCsPbI3
SiO2/Si
Active region
Ag Ag
-2 1 0 -1 2
Voltage/V
Suspension A
=0.48 mm
10-2
10-4
10-6
10-8
10-10
Current/A
(k)
1.0 3.0 1.5 2.5
Flake size/nm
5.0
4.0
1.0
3.0
2.0
Diffusion barrier/eV
(l)
(i)
 Thermionic
e-
Tunneling
MoS2 Ti
Pt
LRS
(j)
 
图 4    (a) 基于材料本征缺陷优化离子传输示意图; (b) SnS的晶体结构示意图; (c) 不同限流下的Ag/SnS/Pt器件的RS特性; (d) SnS
薄膜的扫描隧穿电镜图像; (e) dI/dV与SnS样品偏压关系图[73]; (f) Ag/CsPbI3/Ag忆阻器的结构示意图和SEM图像; (g) Ag/CsPbI3/
Ag忆阻器I-V特性曲线; (h) 碘元素X射线特征峰的能量色散光谱[111]; (i), (j) Pt/MoS2/Ti忆阻器物理机制示意图; (k) MoS2纳
米片尺寸为0.48 μm时的I-V特性曲线; (l) 硫空位扩散势垒随纳米片尺寸变化曲线[117]
Fig. 4. (a) Schematic diagram of ion transport optimization based on intrinsic material defects; (b) schematic diagram of SnS crys-
tal structure; (c) resistive switching of Ag/SnS/Pt device with different compliance current; (d) scanning tunneling microscopy im-
age  of  SnS  thin  film;  (e)  relationship  of  dI/dV  versus  bias  voltage  of  SnS  sample[73];  (f)  schematic  diagram  and  SEM  image  of
Ag/CsPbI3/Ag memristor; (g) I-V characteristic curve of Ag/CsPbI3/Ag memristor; (h) energy-dispersive X-ray spectrum of iodine
elements core level[111]; (i), (j) schematic diagram of the physical mechanism of Pt/MoS2/Ti memristor; (k) I-V characteristic curve
when the size of MoS2 nanosheets is 0.48 μm; (l) curve of the change in sulfur vacancy diffusion barrier with nanosheet size[117].
物 理 学 报   Acta  Phys.  Sin .   Vol.  73, No.  20 (2024 )    207302 
207302-8

和运行能耗100 fJ的超低阈值开关过程(如图4(b),
(c)). 在该器件中, 来自Ag电极的银离子可以占
据SnS层中的Sn空位, 并在外部电场下扩散, 然
后在阴极处还原为银原子, 形成Ag导电通道. 由
于阳离子空位的存在, 降低了银离子从范德瓦耳斯
间隙中的间隙位置移动到Sn空位的迁移势垒, 有
利于更高速和更高能效的电阻切换. 在SnS晶体
中基于Sn空位的缺陷态密度高达1×1018 cm–3, 在
扫描隧道光谱(scanning tunneling spectroscopy,
STS)的微分电导(dI/dV)中可以看到源自类里德
伯(Rydberg-like)束缚空穴状态的受体相关共振
特征. STS光谱中存在一个以–0.4 eV为中心的宽
峰和一个以+0.2 eV为中心的尖峰, 而在没有Sn
缺陷位点的0.9 eV带隙区域中则没有尖峰出现.
在+0.2 eV的正样品偏压下, 受体态移动到费米能
级以上并去离子化以降低注入导带的电子的库
仑 排 斥 力,  从 而 存 在 共 振 尖 峰 (如 图 4(d),  (e)).
Sn缺陷的表观尺寸为372 pm, 远大于Ag+的直径
(252 pm), 这表明Sn空位可以作为SnS中Ag+迁
移的开放通道. 如图4(f), (g)所示, Zhu等[111]采
用Ag/CsPbI3/Ag的器件结构, 实现了超低的开关
电压 (<100 mV)和 超 低 电 流 (1—100 nA).  能 量 
色散X射线光谱(energy-dispersive X-ray spectr-
um, EDXS)表明, 经过重复置位(SET)过程后,
CsPbI3薄膜中的碘离子浓度降低, 这表明忆阻效
应可能源于施加电场下碘空位的产生(图4(h)).
相较于氧空位迁移所需的能垒, 碘离子在CsPbI3
中具备更低的迁移势垒, 可以在低本征缺陷浓度下
实现更低的操作电压[112,113].
晶界区域通常存在较高的缺陷密度, 包括更多
的空位和间隙位. 这些缺陷为离子迁移提供了更多
的路径和更低的能量势垒. Li等[10]采用全溶液法
制备了Pt/CuI/Cu的ECM忆阻器, 展现出超低
的运行电压水平(+0.64/–0.19 V). 密度泛函理论
计算结果表明CuI晶粒内部和晶界(grain boun-
dary,  GB)中 Cu空 位 的 形 成 能 分 别 为 –1.52和
–2.16 eV, 因此CuI中Cu空位应该自然存在, 并
且晶界中的Cu空位密度高于晶粒内部. 同时, 间
隙 位 点 在 内 部 和 晶 界 的 形 成 能 分 别为 3.66和
1.71 eV, Cu间隙位因其仅为0.022 eV迁移能垒
而非常容易占据铜空位, 而铜从铜晶格位扩散到间
隙位的能垒为0.66 eV. 因此铜离子从能量角度实
现高效的漂移路径不会在CuI体材料内部而在于
具备更低局部势垒的晶界处. 由于纯A位阳离子
MA+的钙钛矿在空气中的不稳定性可能在钙钛矿
晶格中引入局部晶格畸变产生空间位阻效应, 阻止
卤素空位等缺陷的迁移路径, 提高迁移所需的活化
能(activation energy, Ea). Liu等[114]采用A位阳
离子混合的方法提升了钙钛矿薄膜结晶度制备了
EGaIn/MACsPbI/PEDOT:PSS/ITO的 忆 阻 器 .
MACsPbI中具备最低Ea(0.58 eV)的碘离子可以
在高结晶度薄膜中沿着八面晶体边缘快速迁移形
成碘空位CFs, 实现了运行电压(+0.48/–0.66 V).
Kim等 [52]的 研 究 通 过 制 备 双 相 的 (Cs3Bi2I9)0.4-
(CsPbI3)0.6, 获得了具备高稳定性的RS器件, 操作
电压仅为0.14 V. 因为由于晶界中的扩展缺陷, 晶
界上的活化能低于在体材料中的活化能. 由于较小
的晶粒会导致更多的晶界, 纳米级晶粒对于快速离
子迁移是有利的[115]. 因此, 可以利用晶界缺陷扩展
来降低活化能, 促进离子快速迁移, 从而降低操作
电压. Chaudhary等[116]报道了一种超薄Ag/WSe2/
Si忆阻器, 显示出均匀的双极RS(+1.8/–0.6 V),
与有缺陷的非晶WSeOx相比, 在单极阈值期间,
实现了10–7的最低关断电流(Ioff)和18.6%的最低
阈值电压(Vth)变化率. 其低电压特性主要归功于
WSe2的缺陷结构较少. 研究表明, 金属离子的扩
散可以通过开关介质内部的缺陷来调节, 并将金
属丝限制在精确的一维通道中. 可以通过控制结
构中的缺陷来调制单极阈值模式和双极模式之间
的变化, 从而实现均匀的开关. 故缺陷较少的忆
阻器能表现出高开关比和最低电压变化的阈值和
双极开关行为. Tang等[117]发现MoS2二维纳米片
能够通过调节层间缺陷扩散过程以改善开关特
性, 而这可以通过薄片尺寸分布来控制(如图4(i),
(j)).  其 中 具 有 最 小 尺 寸 的 MoS2纳 米 片 的 忆 阻 
器表现出最低的运行电压(+0.65 V/–0.90 V)和
周期间切换电压变化, 如图4(k)所示. 通过密度
泛函理论(density functional theory, DFT)计算,
研究人员发现了针对缺陷扩散的迁移势垒的变化,
也即减小MoS2分子尺寸会降低缺陷扩散的能量
障碍(如图4(l)). 这是由于边缘与基面比率的增
大, 较小的纳米片将具有更高的硫空位密度, 使得
硫空位在较小的MoS2薄片中不需要克服较高的
能量障碍, 更容易发生缺陷扩散, 产生更低的电压
操作. 
物 理 学 报   Acta  Phys.  Sin .   Vol.  73, No.  20 (2024 )    207302 
207302-9

4.1.2    本征微纳结构优化离子传输
通过针对性设计和加工不同的微纳结构(如纳
米点、纳米孔等), 改变载流子传输路径和电场分布
以提高电导率或增强局域电场, 已经被证实是降低
工作电压的有效途径之一[87,118–121]. 而通常由其化
学组成、晶体结构和制备条件决定的材料本征微纳
结构通常是最稳定、能量最低的结构, 具有优良的
电学性能; 同时其能够提供自然的导电路径, 减少
额外的界面电阻和散射效应, 进而降低工作电压.
通过自组装和自生长形成纳米线可以被视为
本征微纳结构的代表之一(如图5(a)), 并在神经
形态器件中表现出显著的低功耗优势[122,123]. 如
图5(b)—(d), Lv等[124]利用含有酪氨酸(tyrosine,
Tyr)的环状二肽自组装肽晶体纳米线结构(cyclo
(-Tyr-Tyr) nanowire, c-YY NW)构筑了Ag/c-YY
NW/Ag的平面忆阻器, 在湿度环境下(75% RH)
 
Top electrode(a)
Bottom electrode
Top electrode(i)
Bottom electrode
(b)
(1)
Ag ¹ Ag++e-
(2)
Ag migration
(3)
Ag++e- ¹ Ag
Ag filament
Humidity-mediated ion migration
Tyr as catalyst in (3)
Cyclo(-Tyr-Tyr) (denoted as c-YY)
c-YY nanowire (c-YY NW)
H
N
N
HO
O
HO
OH
Height Potential
1 mm 1 mm
200 nm 0 160 mV 80
(c)
0 0.2 0.4
Voltage/V
10-3
10-6
10-9
10-12
Current/A
(d)
Membrane
potential
(≤100 mV)
Scaled device
10-5
10-3
2 mV/dec
0 0.2
0 50 100 150
Voltage/V
100
80
60
40
20
0
Current/A
(h)
Nanowire film
Ag
SiO2
Pt
(e)
 Nanowires (f)
Top electrode
Bottom electrode
Nanowires
Ag+
Ag
(g)
Conductive filament
(molecule computing site)
Ion migration pathway
Top view
(j)
(k)
010100
001
Top view 40-50 nm
010001
100
(l)
50 nm Adjacent conductive wires
0 9 18 27 36
/nA
0
0.2
0.4
0.6
-axis/
mm -axis/
mm
0.8
1.0
0.8
0.6
0.4
0.2
0
-1.0 -0.5 0.5 1.0 0
Voltage/V
10-7
10-6
10-5
10-4
10-3
Current/A
(m) Switching off
Switching on
 
图 5    基于本征微纳结构优化离子传输　(a) 基于纳米线结构优化离子传输示意图; (b) Ag/c-YY NW/Ag器件结构示意图; (c) c-YY
的化学结构式和开尔文探针力显微镜(KPFM)表面电势分布; (d) 不同限流下Ag/c-YY NW/Ag的阈值开关行为[124]; (e) Ag-SiO2-
Pt器件结构下嵌入图案化蛋白质纳米线薄膜的垂直忆阻器结构; (f) 蛋白质纳米线的TEM图像(标尺为100 nm); (g) 在忆阻器
中引入蛋白质纳米线促进Ag+的阴极还原过程示意图; (h) 蛋白质纳米线器件在800次I-V连续扫描下的阈值开关行为[126]; (i) 基
于高度有序晶体排布的本征微纳结构优化离子传输示意图; (j), (k) PBFCL10薄膜中有序排列的纳米晶体和均匀的离子迁移路径
的示意图; (l) C-AFM表征下PBFCL10薄膜表面的电流分布; (m) Ag/PBFCL10/Au典型I-V特性曲线[131]
Fig. 5. Optimization of ion transport-based on intrinsic nanostructure: (a) Schematic diagram of ion transport optimization based
on intrinsic nanostructure; (b) schematic diagram of Ag/c-YY NW/Ag device structure; (c) chemical structure and KPFM surface
potential distribution of c-YY; (d) threshold switching behavior of Ag/c-YY NW/Ag under different compliance current[124]; (e) ver-
tical  memristor  structure  with  patterned  protein  nanowire  thin  film  embedded  in  Ag-SiO2-Pt  device  structure;  (f)  TEM  image  of
protein  nanowires  (scale  bar:  100 nm);  (g)  schematic  of  the  cathodic  reduction  process  of  Ag+  facilitated  by  protein  nanowires;
(h) threshold switching behavior of protein nanowire devices under 800 consecutive I-V scanning[126]; (i) schematic of ion transport
optimization based on highly-ordered crystal arrangement of intrinsic nanostructures; (j), (k) schematic of ordered nanocrystals and
uniform  ion  migration  pathways  in  PBFCL10  thin  film;  (l)  current  mapping  on  the  surface  of  PBFCL10  film  characterized  by  C-
AFM; (m) typical I-V characteristics of Ag/PBFCL10/Au[131].
物 理 学 报   Acta  Phys.  Sin .   Vol.  73, No.  20 (2024 )    207302 
207302-10

展现出50—100 mV的超低电压阈值开关过程. 在
先前的工作中证明具备微棒结构的二苯丙氨酸肽
自 组 装 晶体 (diphenylalanine-microrod,  FF-MR)
表面的低迁移势垒为活性金属离子提供了定向的
优先传输路径[125]. 在此基础上, Tyr中具备亲水性
的酚羟基官能团为肽自组装纳米线提供了极强的
质子局部积累能力, 从而进一步降低了Ag+的迁移
势垒. 在高湿度条件下, 纳米线表面吸附的水分子
数量更多, 使得负极羟基自由基浓度更高, 从而导
致阳极银离子浓度随之增大以维持电中性. 此外,
质子浓度的增大促进了Ag+的快速迁移, 每次开启
功耗仅为750 fJ. 降低阴极还原电位是降低ECM
忆阻器运行电压的关键, 为此Fu等[126,127]采用了
具备金属还原能力的G硫还原菌的蛋白质纳米线
(protein nanowires, Protein NW)制备了Ag/Pro-
tein NW/Ag扩散型忆阻器, 均匀分散的纳米线实
现了Ag+在垂直方向上的快速还原过程, 表现出
60 mV的超低阈值开关过程如图5(e)—(h)所示.
因此, 在Ag+还原后, 在纳米通道的有限空间中形
成了有序的导电银丝. 值得注意的是, 上述器件所
具备的低金属离子迁移势垒特性虽然可以实现低
电压的快速响应, 但在撤去电压后离子会在化学梯
度和热力梯度影响下的产生自发弛豫过程, 使得纳
米线结构往往适用于实现超低功耗的高速阈值开
关器件.
如图5(i), 具备高度有序晶体排布的本征微纳
结构具备稳定的离子传输能力, 有利于低电压忆阻
器的实现. 高均匀性的迁移势垒分布避免了局部电
场过强, 并且低缺陷密度的高质量结晶减少了离子
自发回迁的位点, 有利于提高非易失性[128–130]. Liu
等[131]合成了聚(呋喃二羧酸丁烯)90-b-(ε-己内酯)10
(poly(butylenefurandicarboxylate)90-b-(ε-capro-
lactone)10, PBFCL10), 由于刚性呋喃基团的存在,
可以通过芳香族部分之间的π-π相互作用实现有
序分子堆积形成晶体, 这些有序密集取向的晶体网
络利于Ag+沿聚合物晶粒边界迁移(图5(j)—(k)).
导电原子力显微镜(C-AFM)中存在局部高电流密
集均匀分布, 相邻CF之间的间距约为40—50 nm
(图5(l)). 以此构筑的超小(50 nm×50 nm)的Au/
PBFCL10/Ag有机忆阻突触可以在±0.2 V完成阻
态切换, 拥有32个可调节的稳定电导状态(>104 s)
(图5(m)). Liu等[132]报道了一种由具有有序纳米
通道的Pt/CuZnS/Ag忆阻纤维制成的纺织型忆
阻器, 展示出高均匀性超低SET电压(≈0.089 V).
其低电压特性主要来源于具有丰富活性硫缺陷的
纳米通道. 在纳米通道内非晶区中的活性缺陷位点
的辅助下, Ag+将优先沿着纳米通道向Pt电极移动. 
4.2    基于掺杂工程的低电压实现策略
忆阻器工作电压与内部离子通量相关, 而离子
通量与基于离子迁移的忆阻器中可移动载流子的
浓度和扩散系数的乘积成正比, 因此增加离子总
量、种类可以有效地降低操作电压. 本节主要关注
通过离子掺杂增加可操控的离子总量和种类的方
法, 以及如何有效地调整材料的导电性质和改善离
子在阻变介质中的高效、稳定传输过程. 
4.2.1    优化离子传输路径
掺杂离子能够增加可操控的离子总量和种类,
可以实现对特定离子传输路径的优化调控[133–135],
(如图6(a)所示). Kim和Lee [136]通过在卡帕-卡拉
胶(κ-carrageenan, κ-car)中引入羧甲基(carboxy-
methyl, CM), 制备了Ag/Ag-doped CM:κ-car/Pt,
实现了低限制电流(10–5 A)、低操作电压(+0.4/
–0.4 V)、 高 速 切 换 (50 ns)以 及 高 开 /关 比 (>103).  Ag
掺杂显著提升了CM:κ-car的离子传导性和氧化速
率, 并提供了额外的Ag+源来增大丝的尺寸和稳定
性, 因而降低了形成导电丝所需的电场强度, 降低
了忆阻器的开关电压(如图6(b), (c)). Wang等[137]
报道了Al/Ti3C2:Ag/Pt忆阻器, 表现出0.2 V的
低操作电压, 单元器件中尖峰突触事件的能耗低
至0.35 pJ. 其低电压源于掺杂在Ti3C2中的银纳
米颗粒. 该方法不仅克服了传统忆阻器由于活性金
属离子随机性问题, 还改善了Ti3C2器件单一数字
型开关过程. Li等[138]展示了一种非传统的基于Ag
掺杂的范德瓦耳斯磷硫化铟(indium phosphorus
sulfide, IPS)存储器, 实现了在低操作电压(~0.2 V)
的高开/关比(~108), 其低电压来源于Ag掺杂使
得Ag离子通过邻近层之间的带电结构性空位的
扩散能垒(0.1433 eV)比通过原始空位(0.3279 eV)
更低, 因此掺杂Ag周围存在更高效的离子扩散路
径(如图6(d), (e)). 这种扩散路径限制了额外导电
通道的形成并稳定了CF. 从而实现了具有低工作
电流、电压的高均匀性RS开关行为.
增加离子来源虽然能够显著地降低运行电压,
但过量的离子迁移会使得性能在非易失性稳定性
物 理 学 报   Acta  Phys.  Sin .   Vol.  73, No.  20 (2024 )    207302 
207302-11

方面下降(例如保留时间). 因此, 离子掺杂策略主
要服务于高速低功耗的TS器件设计, 首要考虑的
是掺杂对象本身的离子迁移率等因素. 如图6(f)所
示, Im等[59]将掺有Ag金属添加剂的MAPbI3前
体溶液旋涂在Au电极衬底上, 由于卤化钙钛矿具
备良好的离子迁移能力, 为避免活性电极的预先扩
散引入了作为阻挡层的PMMA, 采用Ag作为顶
电极. 在此结构下, 器件表现出低阈值电压(~0.2 V)
和40 ns的超快开关速度. 如图6(g)所示, 当施加
的刺激超过阈值电化学能量时, MAPbI3内部分散
的Ag原子可以瞬间聚集并形成CFs. 进而当脉冲
间隔足够长(或停止施压)以使毗邻的Ag+自发扩
散而不是积累时, CFs随着时间推移逐渐分散. 如
图6(h), 相似的活性金属原子分布策略被Jiang
等[139]通过共溅射工艺引入银纳米颗粒构筑掺银氧
化钇稳定氧化锆(yttria stabilized zirconia, YSZ)
 
-0.1 -0.2 0 0.1 0.2
Voltage/V
Reset Set
10-4
10-6
10-8
10-10
Current/A
(c)
(a) Top electrode
Bottom electrode
Top electrode
Bottom electrode
(b)
 Ag doped CM: k-car
Ag+
Pt/Ti
Ag
SiO
2/Si
OSO3-
O
O
O
O
OO
OH OH
CH2COOH
(e)
-0.2 0.6 0.2
Voltage/V
10-16
10-14
10-12
10-10
10-8
10-6
10-4
Current/A
(h)
-1.0 1.0 0
Voltage/V
10-13
10-11
10-9
10-7
10-5
Current/A
(f)
-0.5 0.5 0
Voltage/V
10-12
10-10
10-8
10-6
10-2
10-4
Current/A
(d)
Charge
accumulation
Charge
depletion
Pristine
vacancy
Charged
vacancy
Doped Ag
Charged
vacancy
(g) Threshold firing
Spontaneous relaxation
Ag
Au
Ag
Au
Ag
Au
Ag
Au
As-depositeAs-deposite
Spectrum 1Spectrum 1
Anode
CathodeCathode
Spectrum 2Spectrum 2
(i)(i)
100 nm100 nm
++
++
(j)(j) Post-testPost-test
Spectrum 2Spectrum 2CathodeCathode
AnodeAnode
Spectrum 1Spectrum 1
100 nm100 nm
++
++
(l)
Anode
Cathode
SET

-
-+
+
(k)
Anode
Cathode
Pristine state
 
图 6    (a) 掺杂离子策略——增大离子总量与优化离子传输路径示意图; (b) Ag/Ag掺杂的CM:κ-car/Pt的原理图; (c) Ag/Ag掺
杂的CM:κ-car /Pt器件的典型I-V曲线[136]; (d) Ag-iPS的差分电荷密度分布; (e) Ag/Ag-iPS(~40 nm)/Au忆阻器100次循环内
的I-V曲线[138]; (f) MAPbI3:Ag忆阻器在0 V→1 V→0 V→–1 V→0 V下的双向阈值开关行为; (g) MAPbI3:Ag扩散忆阻器中执行
神经模拟活动的阈值激发和自发弛豫的工作机制示意图[59]; (h) Au/YSZ:Ag/Au/Ti忆阻器连续50个直流电压扫描循环(0→
1.1 V→0 V→–1 V→0 V), 展示出可重复的双向阈值开关行为; (i) TEM观察下的YSZ:Ag忆阻器阈值切换过程, 初始器件具有约25 nm
的大银簇; (j) 直流扫描将银簇分解为约10 nm的小银纳米颗粒, 形成锥形渗透通道; (k), (l) YSZ:Ag忆阻器中Ag团簇演化的初
始状态和加正偏压后的形态[139]
Fig. 6. (a)  Doped  ion  strategy—schematic  diagram  illustrating  increased  total  ion  amount  and  optimized  ion  transport  pathways;
(b) schematic diagram of Ag/Ag-doped CM:κ-car/Pt; (c) typical I-V curve of Ag/Ag-doped CM:κ-car/Pt[136]; (d) differential charge
density  distribution  of  Ag-iPS;  (e)  I-V  curves  within  100 cycles  for  Ag/Ag-iPS  (~40 nm)/Au  memristor[138];  (f)  bidirectional
threshold switching behavior of MAPbI3:Ag memristor under 0 V → 1 V → 0 V → –1 V → 0 V; (g) schematic diagram illustrating
threshold excitation for simulation neural activity and spontaneous relaxation in MAPbI3:Ag diffusion memristor[59]; (h) continuous
50 cycles of DC voltage scans (0 → 1.1 V → 0 V → –1 V → 0 V) in Au/YSZ:Ag/Au/Ti memristor, demonstrating repeatable bidi-
rectional threshold switching behavior; (i) TEM observation of YSZ:Ag memristor threshold switching process, with initial device
featuring large silver clusters (~25 nm); (j) DC scan decomposing silver clusters into smaller silver nanoparticles (~10 nm), form-
ing  conical  permeation  channels;  (k),  (l)  initial  state  and  morphology  after  applying  positive  bias  of  silver  cluster  evolution  in
YSZ:Ag memristor[139].
物 理 学 报   Acta  Phys.  Sin .   Vol.  73, No.  20 (2024 )    207302 
207302-12

的二阶扩散型忆阻器中, 阈值电压低于0.8 V, 开
关比>106. 如图6(i), (j)所示, 其低电压特性主要
来源于银纳米颗粒的重新分布. 在初始阶段, 由于
YSZ是离子迁移率较差的电解质, 银离子的迁移
率和氧化还原利率是有限的, 所以银纳米颗粒可以
以相对稳定的形态分布在介质中. 经过电操作后,
银纳米颗粒在顶部电极和底部电极之间均匀分布,
形成锥形银纳米颗粒渗透路径. 与初始状态的银元
素分布相比, 经过测试后的器件中没有观察到在相
同间隙位置有明显的银元素聚集, 产生更均匀的电
流流动, 减小了局部电阻, 从而降低了电压. Yan等[140]
提出了在制备过程中通过共沉淀将Ag纳米团簇
梯 度 组 装在 TiO2薄 膜 中 (称 为 TiO2:Ag复 合 薄 
膜).  利 用 该 复 合 薄 膜 制 备 了 Ag/TiO2:Ag/Pt器
件, 实现了0.1 V的低操作电压. 这种电导调制与
Ag+在TiO2介质中迁移和重组引起的Ag纳米团
簇间隙的变化有关. 在共溅射过程中Ag团簇在
TiO2薄膜中发生了预分离, 偏压下Ag团簇的局
域电场增强, 从而大大提高了Ag原子在团簇位置
的成核概率, 进一步优化Ag导电丝的结构, 使其
在低电压下实现忆阻器的切换.
掺杂离子会在材料中引入额外的载流子路径,
从而可能增大器件的漏电流. 为此, Tang等[141]
基 于 有 机 无 机 卤 化 物 钙 钛矿 (organic-inorganic
hybrid perovskite, OIHP), 通过银离子掺杂制备
了Au/Ag/PMMA/Ag:OIHP/ITO/聚萘二甲酸乙
二醇酯(polyethylene naphthalate, PEN)忆阻器,
这些预先掺杂的银离子能够迅速响应外部电场, 参
与还原反应形成Ag原子, 因此只需氧化Ag电极
中的一小部分原子即可形成Ag导电通道, 该器件
柔性测试下(弯曲半径为4.7 mm)展现出极低的
漏电流(~50 pA)和低阈值电压(~0.2 V), 具有出色
的超低关态功耗(~200 fW)和开态功耗(~25 nW). 
4.2.2    改善电荷存储释放机制
除直接掺杂金属离子外, 通过离子配位、构相
转变、自掺杂等方式可以有效改变材料电荷存储释
放机制以实现快速、短程的传输过程[59,134,142,143].
Li等[99]将沸石咪唑框架–8(zinc imidazolate fram-
ework-8, ZIF-8)作为稳定的模板, 将Ni前体均匀
地使锚定在ZIF-8的孔隙中有效防止Ni原子的团
聚进而获得NiSAs/N-C. 通过利用均匀分布的捕
获位点、小的隧穿势垒/距离和高电荷能量, Au/
NiSAs/N-C/PVP/ITO忆阻器实现了约0.7 V的
低SET电 压 、 100 ns响 应 速 度 、 大 于 106  s的 稳 
定 保 留 时间 (如 图 7(a)—(c)).  Zhang等 [144]通 过 
超 分 子 自 组 装 策 略 掺 杂 的 无 机 多 金 属 氧 酸盐
(polyoxometalate, POM)簇不仅可以降低聚合物
复合物的能带以更好地俘获电荷, 而且由于其离域
静电吸附特性, 还加速了Ag+的定向传输. 相比于
无掺杂P3HT, 制备的Ag/P3HT@TDA-PW(钼-
磷钨杂多酸, tetrakis(decyl)ammonium phospho-
tungstate)/ITO忆阻器可实现低工作电压(0.34 V).
这种良好的电荷俘获能力和离域静电吸附特性有
助于形成稳定的导电通道, 进而降低导电丝形成所
需的电压. Liu等[145]报道了一种具有生物相容性的
二烷基二硫代磷酸(dialkyl dithiophosphate, DDP)
改性的铜纳米颗粒(CuNPs), 这种有机改性剂在
CuNPs 表面上的存在可视作掺杂剂, 在DFT 模
拟中Cu2+进入DDP-CuNPs膜中与S原子形成金
属键导致绝缘体-金属转变使得带隙消失, 同时在
Pt/DDP-CuNPs/Au器件结构中不稳定Cu—S键
实现了低SET电压(4 mV)阈值开关过程.
Zhang等[146]在丝蛋白(silk fibroin, SF)中掺入
硝酸银(AgNO3), 使得丝蛋白的晶体结构从无序
结构向β-折叠层结构的转变. 在Ag/Silk:AgNO3/
ITO/PET器件结构下实现电压为0.7 V的RS过
程. 载流子倾向于沿着体相SF中形成的微晶传
输, 从而形成相对固定、较短的电子迁移路径(如
图7(d)—(g)). Zhao等[147]在Ag/Silk:AgNO3/Au
结构下, 利用SF中Tyr残留基团对于Ag+的原位
还原过程, 实现了0.17 V的TS过程. 此外, Xia等[148]
报 道 了 结 构为 TiInSnO/BiFeO3/TiN的 忆 阻 器 ,
展现出0.15 V的开关电压、低电阻态约0.46%的
随机涨落和103的开/关比. 其低电压特性得益于
该忆阻器采用了Ti掺杂的铟锡氧化物为顶部电
极材料. 在外场驱动的氧离子迁移过程中, 由于
Ti—O键的高结合能, 这使得其更容易在CF尖端周
围捕获和聚集氧离子(即TiInSnO/BiFeO3界面).
这种积累的氧离子区域使得氧化还原反应变得
局域化可控, 降低了器件整体开关所需的能量.
Mullani等[149]通过热辅助蚀刻和回流合成了新型
的氧化Ti3C2Tx NSs用作阻变功能层, 在低电压
(+1.33/–0.94 V)下实现了高密度存储功能(开关
比>105). 其低电压主要源自于在电极表面进行氧
物 理 学 报   Acta  Phys.  Sin .   Vol.  73, No.  20 (2024 )    207302 
207302-13

化还原反应能够直接改变它的荷电状态. 纳米材料
工程得到的自掺杂结构, 可以提供额外的氧空位进
行迁移, 和银离子迁移生成的银导电细丝共同组成
器件内部的细丝系统, 降低器件开关所需的电压. 
4.3    基于界面优化的低电压实现策略
忆阻器通常由多层材料堆叠组成, 而界面层是
指这些不同材料之间的接触区域(如功能层/电极
层界面、功能层/功能层界面). 在这些界面上, 由
于材料、工艺的不匹配, 容易形成晶格缺陷、氧空
位等, 导致离子在界面处的迁移效率和稳定性下
降. 本节主要讨论如何通过界面工程来优化离子传
输效率, 实现忆阻器稳定高效的低电压特性. 
4.3.1    钝化缺陷进行界面优化
通过增加额外的阻挡层进行界面钝化降低缺
陷密度, 减少在缺陷间传输所需的能量, 可以有效
提升低电压运行可靠性(如图8(a)). 对于钙钛矿材
料而言由于缺陷形成能量低, 过高的缺陷密度会使
得卤素离子获得更多的迁移位点, 这使得器件难以
在低电压操作下保持稳定. 除了采用超薄聚合物
钝化层外(如P3 HT, PMMA等)[150,151], Liu等[152]
根据苯乙基碘化铵(2-phenylethylamine hydroio-
dide, PEAI)对钙钛矿层的钝化作用, 制备出了基
于PET-ITO/MAPbI3/PEAI/Au结 构 的 忆 阻 器 ,
电压可降低到1 V以内. 时间分辨光致发光(time-
resolved photoluminescence, TRPL)测量表明, 钙
钛矿层的衰减时间因钝化而明显延长(图8(b)).
钙钛矿薄膜经过PEAI钝化延长了其载流子寿命
并减少了其缺陷数量. 由于离子在过多的缺陷间传
输会增大能量的消耗, 通过使用PEAI的氨基官能
团可以与钙钛矿的I–结合以占据阳离子空位, 从而
钝化缺陷并抑制膜内的离子迁移. 如图8(c)所示,
在钝化前后对钙钛矿器件通过双对数拟合进行了
空间电荷限制电流(space charge limited current,
SCLC)拟合, 其中陷阱填充极限电压在钝化后从
0.46 V下降到0.21 V. 通过公式计算在原始MAPbI3
中的缺陷密度为3.14×1015 cm–3, 钝化后为1.43×
1015  cm–3[153].  这 降 低 了 每 个 突 触 事 件 消 耗 的 能 
量(13.42 aJ)并可稳定在超高工作频率(15 mV,
4.17 MHz)下表现出动态响应, 是迄今为止报道
的钙钛矿人工突触的最低能耗和最快响应频率
 
(d) (e) (f) (g)
-3 -2 -1 0
Voltage/V
1 210-9
10-7
10-5
Current/A
10-3
10-1
(b)
101 102 103 104 105 106
Time/s
LRS @ 0.1 V
HRS @ 0.1 V
10-7
10-5
Current/A
10-3
10-1
(c)
Trap Microcrystal Elecrton
HRS slope=1 HRS slope > 1 LRS slope > 1 HRS slope=1
(a)
Strong capturing
(charge-deficient effect) Fast speed
Coulomb blockade
(SAs size effect) Long retention
Electron
Ni SAs
Charge-
deficient region
Trapping
 
图 7    掺杂离子策略——改善电荷存储/释放过程　(a) Ni原子周围电荷缺乏区域的差分电荷密度分布表现出超快开关速度和
原子尺寸效应引起的库仑阻塞, 以实现长数据保留能力; (b) Au/NiSAs/N-C/PVP/ITO忆阻器100次循环的I-V特性曲线和(c) 保
留时间[99]; (d)—(g) ITO/Silk:AgNO3/Ag的工作机制模型[146]
Fig. 7. Doped ion strategy—improving charge storage/release processes: (a) Differential charge density distribution around Ni atoms
showing  ultrafast  switching  speed  and  Coulomb  blockade  for  long  retention  due  to  atomic  size  effects;  (b)  the  I-V  characteristic
curves and (c) retention time of 100 cycles of memristor[99]; (d)–(g) mechanism schematic of ITO/Silk:AgNO3/Ag[146].
物 理 学 报   Acta  Phys.  Sin .   Vol.  73, No.  20 (2024 )    207302 
207302-14

(图8(d)). John等[154]采用油酰溴化胍(octanoyl
guanidine  bromide,  OGB)有 机 配 体 与 HP纳 晶
(nanocrystal, NC)界面紧密的结合作用, 在保证HP
NC化学稳定性的同时, 可以为CsPbBr3 NC提供
更好的阻挡层作用, 防止Ag+和Br–的过量电化学
氧化还原反应, 调节导电丝的形成和断裂. 制备的
ITO/PEDOT:PSS/聚 [N,  N'-双 (4-丁 基 苯 基 )-N,  N'-
双苯基联苯胺](poly(4-butylphenyl-diphenyl-ami-
ne,  polyTPD)/OGB-CsPbBr3  NCs/Ag由 于 HP  NC
软晶格中Ag+和Br–的低离子活化能, 在较低的电
压和电流(≤1 V和≤1 µA)下可以完成易失性阈
值开关过程, 表现出超2×106次的循环稳定性.
通过氧化物钝化处理可以减小界面处的缺陷
密度[155]. 如图8(e)—(f), Su等[62]制备了一种包
含MoOx界面层的无铅卤化铯忆阻器(Ag/MoOx/
CsI/Ag), 表现出超低工作电压(<0.18 V). 其低电
压特性主要来源于高缺陷密度的阻变介质中的离
子迁移率明显提升, 从而降低运行所需电压. 在多
晶CsI薄膜中, 不同取向的晶体之间的晶格失配会
产生局部缺陷, 从而形成Ag+的优先扩散路径和
高Ag+迁移率. 如图8(g), 引入MoOx可以阻碍CsI
薄膜的结晶性, 有效限制晶格失配从而控制局部缺
陷密度, 保证了忆阻器低电压驱动的同时具备高稳
定性(>105次). 
4.3.2    保持范德瓦耳斯接触优化界面
保持范德瓦耳斯接触可以促使材料层间达到
最小应力状态, 从而减小界面的粗糙度和缺陷. 对
于二维材料而言, 这意味着层间的原子级平整度得
以保持, 减少界面态密度和散射现象, 降低缺陷数
量以维持高电子迁移率[116,156]. 在金属电极/二维
材料界面接触上, 通过以机械剥离的方式将预设的
金属图案从牺牲层转移到目标基底上, 可以确保金
属/二维材料间的无损vdW接触. 如图9(a)—(c),
Guo等[157]采用vdW金属集成方法构建了具有金
属 电 极 和 二 维 材料 SnSe上 的 超 薄 本 征 氧 化 物
(SnOx)之间vdW接触的忆阻器. 温和的vdW集
成工艺保留了脆弱的SnOx, 并实现了可靠的Ag/
SnOx/SnSe忆阻器, 具有低操作电压(~0.4 V)、高
于103的开关比(如图9(d), (e)). Mao等[158]通过
水辅助金属电极转移技术制备了Au/h-BN/Au忆
阻器, 在0.1 V的电压下实现了107的高开/关比,
且在无电铸器件中实现了低于40 ns的快速切换
速度. vdW/金属接触具有原子级平整的界面、低
 
(b)
MAPbI3+PEAI
MAPbI3
Intensity/arb. units
20 40 60 80
Time/ns
100
Top electrode
Bottom electrode
(a)
MAPbI3+PEAI
MAPbI3
Current/A
0.1 1
Voltage/V
-5
-7
-9
-11
(c) (d)
Current/arb. units
30 25 20 15 10 5 0
Time/ms
4.17 2.94 1.85 1.06 0.87
/MHz
D35 D34 D33 D32 D31
(e)
Ag
Ag +
-
Cesium halide
MoO
LRS
HRS
Conductance/S
0 1.5 1.0 0.5
Number of pulses/105
-1
-2
-3
-4
-5
-6
-7
-8
-9
(g)
Set Reset
Current/A
0.1 0.2 -0.1 -0.3-0.2 0
Voltage/V
-2
-3
-4
-5
-6
-7
-8
-9
-12
-11
-10
-13
(f)
 
图 8    (a) 界面优化策略——钝化界面缺陷示意图; (b) 经过/未经过PEAI钝化的MAPbI3薄膜的时间分辨光致发光光谱; (c) 经
过/未经过PEAI钝化的PET-ITO/MAPbI3/PEAI/Au忆阻器的双对数I-V特性; (d) 在不同频率(4.17, 2.94, 1.85, 1.06, 0.87 MHz)
下的电流响应[152]; (e) Ag/CsI/MoOx/Ag忆阻器示意图; (f) Ag/CsI/MoOx/Ag器件I-V特性; (g) Ag/CsI/MoOx/Ag忆阻器在136000
次循环耐久性测试中的表现[62]
Fig. 8. (a)  Interface  optimization  strategy—passivating  interface  defect  schematic;  (b)  TRPL  spectra  of  MAPbI3  with/without
PEAI passivation; (c) double logarithmic I-V characteristics of PET-ITO/MAPbI3/PEAI/Au memristors with/without PEAI pas-
sivation;  (d)  current  response  at  different  frequencies  (4.17,  2.94,  1.85,  1.06,  0.87 MHz)[152];  (e)  schematic  diagram  of  Ag/CsI/
MoOx/Ag  memristor;  (f)  the  I-V  characteristics  of  Ag/CsI/MoOx/Ag  device;  (g)  endurance  test  of  Ag/CsI/MoOx/Ag  memristors
under 136000 cycles[62].
物 理 学 报   Acta  Phys.  Sin .   Vol.  73, No.  20 (2024 )    207302 
207302-15

界面缺陷密度, 可以提升电子在金属和通道之间的
传输效率, 进而降低开关电压. 通过将不同的二维
材料结合在一起形成的二维范德瓦耳斯异质结结
构由于其独特的稳定性和功能性在解决漏电、光
电响应、环境稳定性方面表现优异[67,159–161]. 在低
电压表现方面, Khot等[162]通过溅射沉积制备了
Ag/GeTe/MoTe2/Pt范 德 瓦 耳 斯 异 质 结 忆 阻 器
(图9(f), (g)), 并在超低开关电压(0.15 V/–0.14 V)
完 成 双极 RS过 程 (图 9(h)),  具 有 极 低 的 能 耗
(≈30 nJ)、长保留时间(104 s)和出色的耐久性(105
次循环). 低电压特性得益于其中Ag电极的氧化
还原过程和层间Te空位的价态变化协同构筑了
开关过程. 
5   基于低电压忆阻器的类脑功能模拟
及计算应用
由于控制膜内外离子交换的细胞膜动作电位
处于超低水平(在50—120 mV), 使得生物神经系
统在传递信息时能量消耗极低, 由此奠定了高能效
的计算基础[126,163]. 在类脑功能模拟研究中, 低电
压忆阻器的操作电压可以与生物神经系统的电压
范围相匹配, 能够精确模拟神经元的电生理活动和
其间隙的突触可塑性, 特别是在可穿戴电子、生物
 
(c) Transferred Ag
SnSe
3 nm
(b)
Ni
Ag
(a)
Ni
Ag
10-4 HRS
LRS
Write
Erase
Read Read
10-5
10-6
10-7
Current/A
op/V
10-8
1
-1
70605040302010 0
0
(e)
0.5
Voltage/V
0 -0.5
(d)8
6
Current/mA
4
2
0
Current/A
10-5
10-7
10-9
10-11
0.5 0 -0.5
(f)
 10-2
(h)
10-3
10-4
Voltage/V
10-5
10-6
-0.3 -0.1 0.1 0.3
10 mm
0
(g)
Ag
SiO2/Si
GeTe
MoTe2
Pt
Ti
20 nm
 
图 9    界面优化策略——保持范德瓦耳斯接触　(a), (b) 将Ag电极转移到SnSe片的另一侧完成Ag/SnOx/SnSe器件; (c) Ag/SnOx/
SnSe界面的横截面TEM图像; (d) Ag/SnOx/SnSe忆阻器I-V 特性曲线; (e) 通过分别施加1 V, –1 V的编程电压脉冲和0.1 V的
读取电压(蓝色曲线), 并仅在读取操作期间测量电流(红色曲线), 演示写入、擦除和读取操作[157]; (f) 在SiO2/Si基板上制造的GeTe/
MoTe2忆阻器示意图; (g) 器件横截面高分辨率TEM图像; (h) 面积在10 μm×10 μm时的I-V特性曲线[162]
Fig. 9. Interface  optimization  strategy—maintaining  van  der  Waals  contact:  (a),  (b)  Ag  electrode  transferred  to  the  other  side  of
SnSe  flake  to  complete  Ag/SnOx/SnSe  device;  (c)  cross-sectional  TEM  image  of  Ag/SnOx/SnSe  interface;  (d)  I-V  characteristic
curve of Ag/SnOx/SnSe memristor; (e) demonstration of write, erase, and read operations by applying programming voltage pulses
of 1 V and –1 V, a reading voltage of 0.1 V (blue curve), and measuring current only during the reading operation (red curve) [157];
(f) schematic diagram of GeTe/MoTe2 memristors fabricated on SiO2/Si substrate; (g) high-resolution cross-sectional TEM image of
device; (h) the I-V characteristic of 10 μm×10 μm memristive device[162].
物 理 学 报   Acta  Phys.  Sin .   Vol.  73, No.  20 (2024 )    207302 
207302-16

接口等领域, 其低功耗、高能效和高精度的计算能
力显得尤为重要. 
5.1    基于低电压忆阻器的神经元功能模拟
及计算应用
图10(a)展示了神经元和细胞膜的基本结构,
研究人员通常以忆阻器在历史操作后的非易失性
程度来确定类脑功能的模拟方向, 通常将非易失性
程度在微秒至秒级的TS器件用于模拟神经元功
能[26]. 如图10(b)所示, 控制脉冲幅值、频率高低
可以在连续输入下通过电导变化模拟神经元动作
电位发放、不应期、敏化-习惯化等基础功能, 这取
决于ECM机制下TS器件中活性金属离子生成
的CFs质量(半径、数量)[60,109,112,139]. 为了进一步
利用TS效应, 可以利用不同类型的传感单元将外
部模拟信号(如机械信号、光信号)转换为电压信
号输入, 进一步搭配简单的电阻-电容电路(包括一
个负载电阻(RL)、一个充电电容(Cm)和一个TS
单元)实现随机漏积整合发放(leaky-integrated-
and-fire,  LIF)响 应 [127](如 图 10(d)—(f)).  值 得 注 
 
(d) Pressure sensor
   L io
m


m
TS
Cell membrane
Neuron
(a)
Open ion
channel
Close ion
channel
150
100
50
0 10 20 30
/s
40 50
io/mV
(e)
20
0
60
40
1.0
0.5
0
0 2 4 6
/s
Press
*Press *Release
8 10
m/V/mA
(f)
(b)
S
AP
0
8
4
0 10 20 30
Time/s
40 50
(c)
Voltage pulse: 1 T=0.6 s,
 0.2 V+1.3 s, 0 V
(h)
ST1
ST2
in
cc
2
Pulse
generator
3
0
REF
1
cc
parallel
c-YY NW
memristor
Moisture sensor
Humidity input
signal
(g)
Breath
Normal
Asthmatics
Tidal volume
Time
Restrictive lung
disease
Abnormal frequency
Abnormal tidal volume
ST1
ST2
l
l
Input Output
Neuron
spikes
Out layer
Hidden layer
3Input
layer
2
10 8
(k)
Accuracy/
%Guess
Ground truth
Normal
Normal Asthmatics Restictive lung
desease
Asthmatics Restictive lung
desease
(l)
Time/s
(i) 0.4
0
0.2
out/V
0.4
0.4
0.2
0
0
0.2
out/Vout/V
Normal
Asthmatics
Restictive lung dsease
Time/s
(j)
Voltage/V
4
2
4
2
4
2
4
2
4
2
4
2
ST1
ST2
 
图 10    基于低电压忆阻器的神经元功能模拟及计算应用　(a) 生物神经元和细胞膜结构; (b), (c) TS器件模拟神经元基本动作
电位发放过程[109]; (d) 将触觉传感单元中输出电压传至人工神经元的电路图; (e), (f) 通过按压压力传感器的电压输入, 人工神经
元中的膜电位(Vm)和电流(I)发生变化[127]; (g) 不同健康个体的呼吸模式; (h) 湿度感知神经元电路示意图; (i) 人工湿度传感神
经元在不同湿度脉冲刺激下的响应; (j) 不同湿度脉冲刺激下的异步ST1和ST2结果; (k) 用于肺部疾病分类的3层神经网络示
意图; (l) 分类结果的混淆矩阵[124]
Fig. 10. Neural function simulation and computational applications based on low-voltage memristors: (a) Biological neurons and cell
membrane  structure;  (b),  (c)  TS  device  simulating  the  basic  action  potential  firing  process  of  neurons[109];  (d)  circuit  diagram  for
transmitting output voltage from tactile sensing unit to artificial neurons; (e), (f) changes in membrane potential (Vm) and current
(I) in artificial neurons due to voltage input from pressure sensor[127]; (g) breathing patterns of different healthy individuals; (h) cir-
cuit  diagram  of  humidity-sensing  neurons;  (i)  response  of  artificial  humidity-sensing  neurons  to  different  humidity  pulse  stimuli;
(j)  asynchronous  ST1 and  ST2 results  under  different  humidity  pulse  stimuli;  (k)  schematic  diagram  of  a  three-layer  neural  net-
work used for lung disease classification; (l) confusion matrix of classification results[124].
物 理 学 报   Acta  Phys.  Sin .   Vol.  73, No.  20 (2024 )    207302 
207302-17

意的是, TS器件的阈值电压(Vth)决定了Cm的充
放电行为, 通过采用在不同环境下(湿度、光线)产
生Vth滑移的TS器件, 可以精准感知环境条件以
进行更智能的决策过程[164,165]. 为实现湿度信号的
感知和原位处理以鉴别呼吸系统疾病, Lv等[124]
利用 Ag/c-YY  NW/Ag在 湿 度 环 境 下 的 低 电 压 
驱 动 能 力 研 究 开 发 了 湿 度 感 知 神 经 元 电路 (如
图10(g), (h)). 该电路利用c-YY纳米线忆阻器和
电路将湿度信号转换为异步脉冲序列, 包括一个感
知神经元、中间放大器、比较器和信号发生器. 对
于 正 常 呼吸 (64%—73%  RH),  神 经 元 在 频 率 约
0.8 Hz下发放电压为0.22 V的脉冲. 随着出气量
增加(如哮喘患者(80%—85% RH)), 频率增大到
约1.2 Hz发放电压为0.17 V的脉冲. 在限制性肺
病的情况下, 异常呼吸率导致发放频率显著增大
(约4.5 Hz), 这一频率增大可归因于湿度变化引起
的Vth滑移(图10(i)). 3种不同输出电压(图10(j),
(k))被转换为异步ST1和ST2信号, 这些信号被
输入到一个3层脉冲神经网络(SNN)中. 图10(l)
显示了210个测试数据集分类的混淆矩阵. 经过
200个周期后所有组别均被正确分类, 证实了所提
出的神经形态感知处理系统的感知-处理一体能力.
基于忆阻器的硬件储备池计算(reservior com-
puting, RC)能效与器件电压密切相关, 用作储备
池结点的单次输入功耗决定了系统完成训练的整
体功耗, 因此利用低电压忆阻器可以完成对于时序
信号的低功耗精准识别过程[27,166]. Zhu等[111]构建
的RC系统利用CsPbI3 TS器件在100 mV脉冲
的不同频率组合方案下产生的电导时序特征, 精准
识别了神经元的放电模式的转变过程和不同神经
元之间的神经同步状态. 
5.2    基于低电压忆阻器的突触功能模拟及
计算应用
如图11(a)—(c)所示, 生物的突触是神经元的
轴突与后神经元的树突连接处的间隙, 与“三明治”
结构的两端忆阻器具备天然的结构相似性. 两者连
接的强度即为突触权重, 突触权重根据前神经元的
输入信号增强或抑制, 这种特性称为突触可塑性[167].
如图11(d), (e), 由于在低压驱动下就可以产生快
速、大量的离子迁移, 所以在脉冲方案设计下突触
后电流响应可以通过脉冲宽度(spiking-duration-
dependent plasticity, SDDP)、个数(spiking-num-
ber-dependent  plasticity,  SNDP)、 频 率 (spiking-
rate-dependent  plasticity,  SRDP)[131,152],  实 现 短 
期 可 塑性 (short-term  plasticity,  STP)[52,82,90,152].
同时, 为了验证低压短期塑性的稳定性, 多循环的
兴奋/抑制测试必要的(如图11(f))[80,90,109]. 这种低
电压驱动的短期塑性在面向动态响应需求的模式
识别系统及应用(如人工传入神经、动态图像识别
等)中有着快速、低功耗优势[168,169].
长时程可塑性(long-term plasticity, LTP)对
于忆阻器在硬件神经网络架构中实现权值映射至
关重要, 这也是忆阻器阵列可以依托基尔霍夫定律
完成矩阵乘加运算的根本[52,82,170]. 对于低压驱动
的BRS器件而言, 内部大量离子发生漂移和复位
时不可避免地会使得器件受焦耳热影响而发生性
能衰减, 因此获取稳定多电导态的方法需要重点考
虑. 如图11(g)所示, Liu等[131]在获取稳定、均匀
的CFs的前提下, 将复位电压逐渐从–0.45 V等量
递增(步长为0.01 V)到–0.76 V, 实现了对一次电
铸生成的CFs的精准能量划分, 得到了32个可区
分的稳定电导态(>104 s). 如图11(h), (i), 这种基
于忆阻器的逐阶切换的过程类似于混沌模拟退火
(chaotic  simulated  annealing,  CSA)算 法 寻 找 全 
局能量最低的思路, 有利于实现决策优化过程. 通
过搭配具有全连接的对称权重矩阵的递归神经网
络(hopfield  neural  network,  HNN),  在 420次 训 
练后实现了对于最优路径的规划过程. 与传统指数
退火相比, 该方法的计算效率提高了31.7%, 准确
率提高了16.7%. 
6   总结与展望
本综述从4个方面总结了面向类脑计算的代
表性低电压忆阻器的进展: 工作机制、典型材料、
调制策略, 以及功能应用. 在总结了低电压忆阻器
工作机制和常见材料的基础上, 重点对各种类型的
低电压忆阻器的实现策略进行了详细分析, 包括:
1) 从材料特性出发, 通过本征缺陷和本征微纳结
构实现高效离子传输; 2) 从物理机制出发, 通过掺
杂工程优化离子传输路径或改善电荷存储释放机
制; 3) 从器件结构出发, 通过钝化缺陷、保持范德
瓦耳斯接触进行界面优化, 以上策略为未来实际应
用中降低忆阻器电压提供了思路和方向. 此外, 低
电压忆阻器的操作电压可以与生物神经系统的电
物 理 学 报   Acta  Phys.  Sin .   Vol.  73, No.  20 (2024 )    207302 
207302-18

压范围相匹配, 能够精确模拟神经元和突触功能,
并在生物接口、可穿戴电子应用中表现出能耗优
势. 尽管低电压忆阻器的研究取得了阶段性进展,
但仍然存在一些障碍需要克服.
1) 低电压的阻变机制仍存在局限性
在低电压下, 驱动离子或电子在材料中移动的
效率会显著降低, 需要进一步研究新的机制和材料
来增强低电压下的传输效率. 尽管导电细丝型阻变
机制已经得到了相对深入的研究和理解, 但细丝软
击穿随机性、脆弱性的本质限制了低电压的稳定实
现. 界面型机制温和、均匀的开关过程可以为稳定
性提供保证, 但响应速度低、非易失性稳定性仍有
不足. 目前, 低电压器件的物理机制与其性能之间
的具体对应关系尚未完全明晰, 需要从物理机制角
 
10 20 30 80 90 100
Time/s
6 MAPbI3
   
   
MAPbI3+PEAI
4
2
0
0.6
(d)
0.4
0.2 Current/nA
0 Current/nA
(e)
0 20 70 80
Time/s Pulse number (#)
6 MAPbI3
1 2
1 2
MAPbI3+PEAI
4
2
0
0.6
0.4
0.2 Current/nA
0 Current/nA
(f)
200 250 1750 1800
MAPbI3+PEAI
0.3
0.2
Current/nA0.1
0
Perovskite artificial synapse
(a) (b) (c)
Pre-neuron
Pre-neuron
Synapse
ITO/PET
PEAI
MAPbI3
15
QC(0)
Voltage/V
9
3
0
-0.6
0 5 10 15 20
Switching number (#)
25 30
(g)
(h)
Final state (420th time) (i)
Map with path
0 1 2 3 4 5 6 7 8 9
9
8
7
6
5
4
3
2
1
0
1(j)
(j) 32
32
(i)
32
(i)
32
Weight Output
1.00
0.75
0.50
0.25
10-4
0
1.0
0.8
0.6
0.4
0.2
0
230.7 mW 238.4 mW 258.5 mW =0T(14.85-0.38), 2=0.9968
Reset
Reset
Au +
Ag -
~f
~f
266.6 mW 261.0 mW
243.7 mW
228.2 mW
199.6 mW 175.6 mW 138.7 mW
Au +
Ag -
Linear
Exponential
Bioinspired
Energy
Self-feedback
Xinin
inin
in
in
in
in
X
XX
X
X
X
XX
W
…
W
I
S ò
 
图 11    基于低电压忆阻器的突触功能模拟及计算应用 (a)—(c) 生物突触与忆阻器结构相似性示意图; (d) PET-ITO/MAPbI3/
PEAI/Au忆阻器在具有不同的持续时间的单个脉冲下的SDDP行为(d1 = 68 ms, d2= 136 ms, d3 = 545 ms, d4 = 615 ms), 电压
保持为–0.5 V; (e) 在具有不同频率的连续脉冲下的SRDP行为(f1 = 1.06 Hz, f2 = 6.39 Hz), 每组脉冲为10个, 电压保持为
–0.5 V, 脉宽为68 ms; (f) 增强和抑制的循环[152]; (g) Au/PBFCL10/Ag忆阻器电导连续调制过程; (h) 具有自反馈的HNN结合了
基于线性、指数和忆阻器的CSA算法; (i) 在420次迭代后, 使用HNN网络预测的突触权重矩阵、输出矩阵和行进路线的结果[131]
Fig. 11. Based  on  the  low-voltage  memristor  synaptic  function  simulation  and  computational  applications:  (a)–(c)  Schematic  dia-
gram of the similarity between biological synapses and memristor structures; (d) SDDP behavior of PET-ITO/MAPbI3/PEAI/Au
memristor under a single pulse with different durations (d1 = 68 ms, d2 = 136 ms, d3 = 545 ms, d4 = 615 ms) while maintaining a
voltage of –0.5 V; (e) SRDP behavior under continuous pulses with different frequencies (f1 = 1.06 Hz, f2 = 6.39 Hz), each consist-
ing  of  10 pulses,  while  maintaining  a  voltage  of  –0.5 V  and  a  pulse  width  of  68 ms;  (f)  enhancement  and  inhibition  cycles[152];
(g) conductive modulation process of Au/PBFCL10/Ag memristor; (h) HNN with self-feedback combining linear, exponential, and
memristor-based CSA algorithms; (i) results of synaptic weight matrix, output matrix, and path prediction using the HNN network
after 420 iterations[131].
物 理 学 报   Acta  Phys.  Sin .   Vol.  73, No.  20 (2024 )    207302 
207302-19

度如相变[173]、铁电隧穿[174]、磁自旋[175]等其他机
制出发, 发掘更高速、更稳定的优势机制, 进一步
实现高密度集成低电压忆阻器阵列, 提升存内计算
的整体能效.
2) 低电压忆阻器稳定性仍需进一步提升
尽管现有工作已经考虑在追求低电压特性的
同时兼顾忆阻器的其他稳定性参数, 如大范围的开
关比、稳定的保持时间以及循环耐久性[17–19]. 但高
离子电子传输效率下, 低电压忆阻器在实际应用中
表现出一些显著的非理想特性, 如较高的噪声水
平、阻态漂移以及显著的热效应, 这些问题严重制
约了其在人工神经网络中的操作精度和能耗表现[6,13].
此外电压大小与写入时间存在的固有矛盾决定了
开关状态的稳定性和写入/读取速度[176], 即在保证
写入速度的同时, 确保数据的长期稳定性. 这种矛
盾的根源通常与电场相关的离子迁移率或温度诱
导的离子迁移率有关. 高电压下驱动的离子非线性
动力过程具备显著的高迁移率, 从而实现快速写
入, 因此需要增大低电压下的离子迁移速度. 同时
由于电压输入范围的缩小, 电阻变化的线性区和非
线性区界限模糊, 读取电压的选取也是至关重要.
这需要通过进一步的创新结构设计和材料选择来
找到平衡点, 以满足实际应用中对稳定性和持久性
的高要求.
3) 低电压的应用场景有待探索
为了挖掘低电压忆阻器最适合的应用场景, 需
要进行更加深入和系统的研究, 理解其在不同条
件下的物理过程. 此外, 当前低电压忆阻器的应用
场景相对有限, 主要集中在某些特定领域. 为了拓
宽其应用范围, 可以考虑通过多物理场调制(如
光[177–179]、热[180,181]等)来实现对低电压忆阻器性
能的灵活调控, 从而满足更多元化的应用需求, 实
现更智能的感知-计算过程.
4) 低电压在电路应用方面存在限制
在交叉阵列结构中串扰、潜行电流等问题成为
限制集成规模的关键因素之一, 忆阻器单元通常需
要结合晶体管、选通器进行工作(1T1R, 1S1R)[182].
受到输入电压范围的限制, 低压忆阻器与晶体管或
选通器的电压匹配阻碍了大规模电路应用. 随着低
电压范围进一步缩小(小于毫伏), 还需要具备低噪
声的测试环境、开发有效的噪声滤除及信号放大的
外围电路实现微小信号的输入与探测. 因此, 如何
克服这些挑战, 实现低电压忆阻器的高效集成, 是
未来研究的重要方向. 这不仅需要在材料和器件设
计上进行创新, 还需要开发新的电路架构和信号处
理技术, 提高集成密度和系统的整体性能. 通过这
些努力, 可以为低电压忆阻器在复杂电路系统中的
应用开辟新的道路.
随着新兴信息技术的快速发展, 数据存储和计
算的需求持续增长, 忆阻器将在未来各种研究领域
中发挥日益重要的作用. 尽管低电压忆阻器的应用
开发仍处于初级阶段, 如果上述问题能够得到改
善, 现有研究工作将对高能效人工神经形态计算奠
定坚实的基础.
参考文献 
 Di Ventra M, Pershin Y V 2013 Nat. Phys. 9 200[1]
 Valov  I,  Linn  E,  Tappertzhofen  S,  Schmelzer  S,  van  den 
Hurk J, Lentz F, Waser R 2013 Nat. Commun. 4 1771
[2]
 Jo S H, Chang T, Ebong I, Bhadviya B B, Mazumder P, Lu 
W 2010 Nano Lett. 10 1297
[3]
 Zhang X M, Zhuo Y, Luo Q, Wu Z H, Midya R, Wang Z R, 
Song  W  H,  Wang  R,  Upadhyay  N  K,  Fang  Y  L,  Kiani  F,
Rao M Y, Yang Y, Xia Q F, Liu Q, Liu M, Yang J J  2020
Nat. Commun. 11 51
[4]
 Li  X  Y,  Tang  J  S,  Zhang  Q  T,  Gao  B,  Yang  J  J,  Song  S,
Wu W, Zhang W Q, Yao P, Deng N, Deng L, Xie Y, Qian 
H, Wu H Q 2020 Nat. Nanotechnol. 15 776
[5]
 Choi S, Yang J, Wang G 2020 Adv. Mater. 32 2004659[6]
 He  K,  Liu  Y  Q,  Yu  J  C,  Guo  X  T,  Wang  M,  Zhang  L  D,
Wan C J, Wang T, Zhou C J, Chen X D  2022 ACS Nano 16
9691
[7]
 Kim N, Oh J, Kim S, Cha J H, Choi J, Im S G, Choi S Y, 
Jang B C 2024 Adv. Funct. Mater. 34 2305136
[8]
 Yang J Q, Zhang F, Xiao H M, Wang Z P, Xie P, Feng Z H,
Wang J J, Mao J Y, Zhou Y, Han S T  2022 ACS Nano 16
21324
[9]
 Li B, Wei W, Luo L, Gao M, Yu Z G, Li S, Ang K W, Zhu 
C 2022 Adv. Electron. Mater. 8 2200089
[10]
 Zhao H, Liu Z W, Tang J S, Gao B, Qin Q, Li J M, Zhou Y,
Yao  P,  Xi  Y,  Lin  Y  D,  Qian  H,  Wu  H  Q   2023  Nat.
Commun. 14 2276
[11]
 Cai B Q, Huang Y, Tang L Z, Wang T Y, Wang C, Sun Q 
Q, Zhang D W, Chen L 2023 Adv. Funct. Mater. 33 2306272
[12]
 Duan H, Cheng S Q, Qin L, Zhang X L, Xie B Y, Zhang Y, 
Jie W J 2022 J. Phys. Chem. Lett. 13 7130
[13]
 Eberhardt D T 1989  International 1989 Joint Conference on
Neural  Networks  Washington,  DC,  USA,  June  18-22,  1989
pp183-190
[14]
 Calimera A, Macii E, Poncino M 2013 Funct Neurol. 28 191[15]
 Andreou  A  G,  Meitzler  R  C,  Strohbehn  K,  Boahen  K  A 
1995 Neural Networks 8 1323
[16]
 Song M K, Kang J H, Zhang X Y, Ji W, Ascoli A, Messaris 
I,  Demirkol  A  S,  Dong  B,  Aggarwal  S,  Wan  W  2023  ACS
Nano 17 11994
[17]
 Park Y J, Lee J S 2022 J. Phys. Chem. Lett. 13 5638[18]
 Wang J J, Qian F S, Huang S M, Lv Z Y, Wang Y, Xing X 
C,  Chen  M,  Han  S  T,  Zhou  Y   2020  Adv.  Intell.  Syst.  3
2000180
[19]
物 理 学 报   Acta  Phys.  Sin .   Vol.  73, No.  20 (2024 )    207302 
207302-20

 Hirose Y, Hirose H 1976 J. Appl. Phys. Vol. 47 2767[20]
 Waser R, Aono M 2007 Nat. Mater. 6 833[21]
 Strukov D B, Snider G S, Stewart D R, Williams R S  2008
Nature 453 80
[22]
 Vasilopoulou M, Mohd Yusoff A R b, Chai Y, Kourtis M A, 
Matsushima  T,  Gasparini  N,  Du  R,  Gao  F,  Nazeeruddin  M
K, Anthopoulos T D, Noh Y Y 2023 Nat. Electron. 6 949
[23]
 Cheng P, Sun K, Hu Y H 2016 Nano Lett. 16 572[24]
 Lin  W  P,  Liu  S  J,  Gong  T,  Zhao  Q,  Huang  W  2014  Adv.
Mater. 26 570
[25]
 Kumar  S,  Wang  X,  Strachan  J  P,  Yang  Y,  Lu  W  D  2022
Nat. Rev. Mater. 7 575
[26]
 Moon J, Ma W, Shin J H, Cai F, Du C, Lee S H, Lu W D 
2019 Nat. Electron. 2 480
[27]
 West  W  C,  Sieradzki  K,  Kardynal  B,  Kozicki  M  N  1998  J.
Electrochem. Soc. 145 2971
[28]
 Yang Y C, Gao P, Li L, Pan X Q, Tappertzhofen S, Choi S, 
Waser R, Valov I, Lu W D 2014 Nat. Commun. 5 4232
[29]
 Zhu  J  D,  Zhang  T,  Yang  Y  Y,  Huang  R  2020  Appl. Phys.
Rev. 7 011312
[30]
 Xu W T, Cho H C, Kim Y H, Kim Y T, Wolf C, Park C G, 
Lee T o 2016 Adv. Mater. 28 5916
[31]
 Xiao Z G, Huang J S 2016 Adv. Electron. Mater. 2 1600100[32]
 Sawa A 2008 Mater. Today 11 28[33]
 Rao M Y, Tang H, Wu J B, Song W H, Zhang M, Yin W B, 
Zhuo Y, Kiani F, Chen B, Jiang X Q, Liu H F, Chen H Y, 
Midya R, Ye F, Jiang H, Wang Z R, Wu M C, Hu M, Wang 
H, Xia Q F, Ge N, Li J, Yang J J 2023 Nature 615 823
[34]
 Song W H, Rao M Y, Li Y N, Li C, Zhuo Y, Cai F X, Wu 
M C, Yin W B, Li Z Z, Wei Q 2024 Science 383 903
[35]
 Yang  J  J,  Strukov  D  B,  Stewart  D  R   2012  Nat.
Nanotechnol. 8 13
[36]
 Li Z N, Tian B Y, Xue K H, Wang B, Xu M, Lu H, Sun H 
J, Miao X S 2019 IEEE Electron Device Lett. 40 1068
[37]
 Carlos  E,  Deuermeier  J,  Branquinho  R,  Gaspar  C,  Martins
R, Kiazadeh A, Fortunato E 2021 J. Mater. Chem. C 9 3911
[38]
 Bian L Y, Xie M, Chong H, Zhang Z W, Liu G Y, Han Q S, 
Ge  J  Y,  Liu  Z,  Lei  Y,  Zhang  G  W,  Xie  L  H  2022  Chin. J.
Chem. 40 2451
[39]
 Yue J L, Zou L Q, Bai N, Zhu C Q, Yi Y H, Xue F, Sun H 
J,  Hu  S,  Cheng  W  M,  He  Q  2024   Small  Methods  n/a
2301657
[40]
 Saleem  A,  Kumar  D,  Singh  A,  Rajasekaran  S,  Tseng  T  Y
2022 Adv. Mater. Technol. 7 2101208
[41]
 Yoon J H, Zhang J M, Ren X C, Wang Z R, Wu H Q, Li Z 
Y,  Barnell  M,  Wu  Q,  Lauhon  L  J,  Xia  Q  F   2017  Adv.
Funct. Mater. 27 1702010
[42]
 Li Y, Chu J X, Duan W J, Cai G S, Fan X H, Wang X Z, 
Wang  G,  Pei  Y  L   2018  ACS  Appl.  Mater.  Interfaces  10
24598
[43]
 She Y, Wang F, Zhao X Y, Zhang Z Z, Li C, Pan H G, Hu 
K,  Song  Z  T,  Zhang  K  L   2021  IEEE  Trans.  Electron
Devices 68 1950
[44]
 Yuan R, Tiw P J, Cai L, Yang Z Y, Liu C, Zhang T, Ge C, 
Huang R, Yang Y C 2023 Nat. Commun. 14 3695
[45]
 Yang K, Wang Y H, Tiw P J, Wang C M, Zou X L, Yuan 
R, Liu C, Li G, Ge C, Wu S, Zhang T, Huang R, Yang Y C 
2024 Nat. Commun. 15 1693
[46]
 Fu Y Y, Zhou Y, Huang X D, Dong B Y, Zhuge F W, Li Y, 
He  Y  H,  Chai  Y,  Miao  X  S  2022  Adv.  Funct.  Mater.  32
2111996
[47]
 Liu  Z  H,  Cheng  P  P,  Kang  R  Y,  Zhou  J,  Zhao  X,  Zhao  J,
Zuo Z Y 2023 Adv. Mater. Interfaces 10 2201513
[48]
 Sun K X, Wang Q R, Zhou L, Wang J J, Chang J J, Guo R,
Tay B K, Yan X B 2023 Sci. China Mater. 66 2013
[49]
 Berruet M, Pérez -Martínez J C, Romero B, Gonzales C, Al -
Mayouf A M, Guerrero A, Bisquert J 2022 ACS Energy Lett.
7 1214
[50]
 Huang F C, Ge S P, Wei R L, He J Q, Ma X L, Tao J, Lu 
Q C, Mo X M, Wang C F, Pan C F  2022 ACS Appl. Mater.
Interfaces 14 43474
[51]
 Kim S G, Van Le Q, Han J S, Kim H, Choi M J, Lee S A, 
Kim T L, Kim S B, Kim S Y, Jang H W  2019 Adv. Funct.
Mater. 29 1906686
[52]
 Abbas G, Hassan M, Khan Q, Wang H F, Zhou G G, Zubair 
M, Xu X R, Peng Z C 2022 Adv. Electron. Mater. 8 2101412
[53]
 John  R  A,  Shah  N,  Vishwanath  S  K,  Ng  S  E,  Febriansyah
B,  Jagadeeswararao  M,  Chang  C  H,  Basu  A,  Mathews  N 
2021 Nat. Commun. 12 3681
[54]
 Cheng X F, Qian W H, Wang J, Yu C, He J H, Li H, Xu Q 
F, Chen D Y, Li N J, Lu J M 2019 Small 15 1905731
[55]
 Zeng F J, Guo Y Y, Hu W, Tan Y Q, Zhang X M, Feng J 
L, Tang X S 2020 ACS Appl. Mater. Interfaces 12 23094
[56]
 Ren Y Y, Bu X B, Wang M, Gong Y, Wang J J, Yang Y Y, 
Li G J, Zhang M, Zhou Y, Han S T  2022 Nat. Commun. 13
5585
[57]
 Lao J, Xu W, Jiang C L, Zhong N, Tian B B, Lin H C, Luo 
C  H,  Travas-sejdic  J,  Peng  H,  Duan  C  G  2021  J.  Mater.
Chem. C 9 5706
[58]
 Im  I  H,  Baek  J  H,  Kim  S  J,  Kim  J,  Park  S  H,  Kim  J  Y,
Yang J J, Jang H W 2023 Adv. Mater. 36 2307334
[59]
 Li  J  X,  Yang  Y  C,  Yin  M  H,  Sun  X  H,  Li  L  D,  Huang  R
2020 Mater. Horiz. 7 71
[60]
 Mishra D, Mokurala K, Kumar A, Seo S G, Jo H B, Jin S H 
2022 Adv. Funct. Mater. 33 2211022
[61]
 Su T K, Cheng W K, Chen C Y, Wang W C, Chuang Y T, 
Tan G H, Lin H C, Hou C H, Liu C M, Chang Y C, Shyue J
J, Wu K C, Lin H W 2022 ACS Nano 16 12979
[62]
 Xu R J, Jang H, Lee M H, Amanov D, Cho Y, Kim H, Park 
S, Shin H J, Ham D 2019 Nano Lett. 19 2411
[63]
 Yin L, Cheng R Q, Wen Y, Zhai B X, Jiang J, Wang H, Liu 
C S, He J 2022 Adv. Mater. 34 2108313
[64]
 Wang Y S, Liu H W, Liu P, Lu W L, Cui J Q, Chen X Y, 
Lu M 2022 J. Alloys Compd. 909 164775
[65]
 Wu X H, Ge R J, Chen P A, Chou H, Zhang Z P, Zhang Y 
F,  Banerjee  S,  Chiang  M  H,  Lee  J  C,  Akinwande  D  2019
Adv. Mater. 31 1806790
[66]
 Liu X L, Zhang C, Li E L, Gao C F, Wang R X, Liu Y, Liu 
F C, Shi W, Yuan Y H, Sun J, Lin Y F, Chu J H, Li W W 
2024 Adv. Funct. Mater. 34 2309642
[67]
 Chen  H  H,  Kang  Y,  Pu  D,  Tian  M,  Wan  N,  Xu  Y,  Yu  B,
Jie W J, Zhao Y D 2023 Nanoscale 15 4309
[68]
 Bertolazzi  S,  Bondavalli  P,  Roche  S,  San  T,  Choi  S  Y, 
Colombo  L,  Samorì  P,  Bonaccorso  F  2019  Adv.  Mater.  31
1806663
[69]
 Desai S B, Madhvapathy S R, Sachid A B, Llinas J P, Wang
Q,  Ahn  G  H,  Pitner  G,  Kim  M  J,  Bokor  J,  Hu  C   2016
Science 354 99
[70]
 Kim S, Konar A, Hwang W S, Lee J H, Lee J, Yang J, Jung 
C, Kim H, Yoo J B, Choi J Y 2012 Nat. Commun. 3 1011
[71]
 Gosai J, Patel M, Liu L, Lokhandwala A, Thakkar P, Chee 
M Y, Jain M, Lew W S, Chaudhari N, Solanki A  2024 ACS
Appl. Mater. Interfaces 16 17821
[72]
 Lu X F, Zhang Y S, Wang N Z, Luo S, Peng K L, Wang L, 
Chen H, Gao W B, Chen X H, Bao Y, Liang G c, Loh K P 
2021 Nano Lett. 21 8800
[73]
物 理 学 报   Acta  Phys.  Sin .   Vol.  73, No.  20 (2024 )    207302 
207302-21

 Sun Y J, Zhang R J, Teng C J, Tan J Y, Zhang Z H, Li S 
N, Wang J W, Zhao S L, Chen W J, Liu B L, Cheng H M 
2023 Mater. Today 66 9
[74]
 Zhao H, Dong Z P, Tian H, DiMarzi D, Han M G, Zhang L 
H, Yan X D, Liu F X, Shen L, Han S J  2017 Adv. Mater. 29
1703232
[75]
 Eda G, Fanchini G, Chhowalla M  2008 Nat. Nanotechnol. 3
270
[76]
 Wang  J,  Liang  M  H,  Fang  Y,  Qiu  T  F,  Zhang  J,  Zhi  L  J
2012 Adv. Mater. 24 2874
[77]
 Sun Q J, Kim D H, Park S S, Lee N Y, Zhang Y, Lee J H, 
Cho K, Cho J H 2014 Adv. Mater. 26 4735
[78]
 Wang K Y, Li L T, Zhao R J, Zhao J H, Zhou Z Y, Wang J 
J, Wang H, Tang B K, Lu C, Lou J Z, Chen J S, Yan X B 
2020 Adv. Electron. Mater. 6 1901342
[79]
 Li S F, Pam M E, Li Y S, Chen L, Chien Y C, Fong X Y, 
Chi D Z, Ang K W 2022 Adv. Mater. 34 2103376
[80]
 Feng  X  W,  Li  Y  D,  Wang  L,  Chen  S,  Yu  Z  G,  Tan  W  C,
Macadam N, Hu G H, Huang L, Chen L, Gong X, Chi D Z, 
Hasan T, Thean A V Y, Zhang Y W, Ang K W  2019 Adv.
Electron. Mater. 5 1900740
[81]
 Shi Y Y, Liang X H, Yuan B, Chen V, Li H T, Hui F, Yu Z 
C  W,  Yuan  F,  Pop  E,  Wong  H  S  P,  Lanza  M  2018  Nat.
Electron. 1 458
[82]
 Ding  G  L,  Chen  R  S,  Xie  P,  Yang  B  D,  Shang  G,  Liu  Y,
Gao L L, Mo W A, Zhou K, Han S T, Zhou Y 2022 Small 18
2200185
[83]
 Nikam R D, Rajput K G, Hwang H 2021 Small 17 2006760[84]
 Ling  S  T,  Zhang  C,  Ma  C  L,  Li  Y,  Zhang  Q  C  2022  Adv.
Funct. Mater. 33 2208320
[85]
 Wang  K,  Dai  S  L,  Zhao  Y  W,  Wang  Y,  Liu  C,  Huang  J
2019 Small 15 1900010
[86]
 Yan X B, Wang K Y, Zhao J H, Zhou Z Y, Wang H, Wang 
J J, Zhang L, Li X Y, Xiao Z, Zhao Q L, Pei Y F, Wang G, 
Qin  C  Y,  Li  H,  Lou  J  Z,  Liu  Q,  Zhou  P   2019  Small  15
1900107
[87]
 Sokolov  A,  Ali  M,  Li  H,  Jeon  Y  R,  Ko  M  J,  Choi  C  2020
Adv. Electron. Mater. 7 2000866
[88]
 He  N,  Zhang  Q  Q,  Tao  L  Y,  Chen  X  T,  Qin  Q,  Liu  X  Y,
Lian X J, Wan X, Hu E, Xu J G, Xu F, Tong Y  2021 IEEE
Electron Device Lett. 42 319
[89]
 Wang T Y, Meng J L, Zhou X F, Liu Y, He Z Y, Han Q, Li 
Q X, Yu J J, Li Z H, Liu Y K, Zhu H, Sun Q Q, Zhang D 
W,  Chen  P  N,  Peng  H  S,  Chen  L  2022  Nat. Commun.  13
7432
[90]
 Ahmed T, Kuriakose S, Tawfik S A, Mayes E L, Mazumder 
A, Balendhran S, Spencer M J, Akinwande D, Bhaskaran M, 
Sriram S, Walia S 2022 Adv. Funct. Mater. 32 2107068
[91]
 Ouyang  J  Y,  Chu  C  W,  Szmanda  C  R,  Ma  L  P,  Yang  Y
2004 Nat. Mater. 3 918
[92]
 Hota  M  K,  Bera  M  K,  Kundu  B,  Kundu  S  C,  Maiti  C  K
2012 Adv. Funct. Mater. 22 4493
[93]
 Li S Z, Zeng F, Chen C, Liu H Y, Tang G S, Gao S, Song C,
Lin Y S, Pan F, Guo D 2013 J. Mater. Chem. C 1 5292
[94]
 Li J Y, Qian Y Z, Li W, Yu S C, Ke Y X, Qian H W, Lin Y 
H, Hou C H, Shyue J J, Zhou J, Chen Y, Xu J P, Zhu J T, 
Yi M D, Huang W 2023 Adv. Mater. 35 2209728
[95]
 Luo X L, Ming J Y, Gao J C, Zhuang J W, Fu J W, Ren Z 
H, Ling H F, Xie L H 2022 Front. Neurosci. 16
[96]
 Wang  L,  Qu  J  X,  Li  J  Z,  Wen  D  Z   2023  Adv.  Mater.
Technol. 8 2201540
[97]
 Wang L, Yang J, Zhang X F, Wen D Z  2023 Nanomaterials
13 3021
[98]
 Li  H  X,  Li  Q  X,  Li  F  Z,  Liu  J  P,  Gong  G  D,  Zhang  Y  Q,
Leng  Y  B,  Sun  T,  Zhou  Y,  Han  S  T  2023  Adv. Mater.  36
2308153
[99]
 Shaikh  M  T  A  S,  Nguyen  T  H  V,  Jeon  H  J,  Prasad  C  V,
Kim  K  J,  Jo  E  S,  Kim  S,  Rim  Y  S   2024  Adv.  Sci.  11
2306206
[100]
 Wang Z Y, Wang L Y, Wu Y M, Bian L Y, Nagai M, Jv R 
L,  Xie  L  H,  Ling  H  F,  Li  Q,  Bian  H  Y,  Yi  M  D,  Shi  N  E,
Liu X G, Huang W 2021 Adv. Mater. 33 2104370
[101]
 Zhou J, Li W, Chen Y, Lin Y H, Yi M D, Li J Y, Qian Y Z, 
Guo Y, Cao K Y, Xie L H, Ling H F, Ren Z J, Xu J P, Zhu 
J T, Yan S K, Huang W 2020 Adv. Mater. 33 2006201
[102]
 Yan X B, Li X Y, Zhou Z Y, Zhao J H, Wang H, Wang J J, 
Zhang  L,  Ren  D  L,  Zhang  X,  Chen  J  S  2019  ACS  Appl.
Mater. Interfaces 11 18654
[103]
 Lin Y, Xu H Y, Wang Z Q, Cong T, Liu W Z, Ma H L, Liu 
Y C 2017 Appl. Phys. Lett. 110 193503
[104]
 Liu S Z, He Z L, Zhang B, Zhong X L, Guo B J, Chen W L, 
Duan H X, Tong Y, He H D, Chen Y, Liu G  2023 Adv. Sci.
10 2305075
[105]
 Zhou G D, Li J, Song Q L, Wang L D, Ren Z J, Sun B, Hu 
X F, Wang W H, Xu G B, Chen X D, Cheng L, Zhou F C, 
Duan S K 2023 Nat. Commun. 14 8489
[106]
 Wang  R,  Wang  S  S,  Xin  Y  H,  Cao  Y  X,  Liang  Y,  Peng  Y
Q, Feng J, Li Y, Lv L, Ma X H, Wang H, Hao Y  2023 Small
Sci. 3 2200082
[107]
 Oh J, Yang S Y, Kim S, Lee C, Cha J H, Jang B C, Im S G,
Choi S Y 2023 Mater. Horiz. 10 2035
[108]
 Zhang T, Wang L Y, Ding W W, Zhu Y F, Qian H W, Zhou
J, Chen Y, Li J Y, Li W, Huang L Y, Song C Y, Yi M D, 
Huang W 2023 Adv. Mater. 35 2302863
[109]
 Wang Y L, Su J, Ouyang G Y, Geng S Y, Ren M C, Pan W 
L, Bian J, Cao M H 2024 Adv. Funct. Mater. 34 2316397
[110]
 Zhu X J, Wang Q W, Lu W D 2020 Nat. Commun. 11 2439[111]
 Zhu X J, Lee J H, Lu W D 2017 Adv. Mater. 29 1700527[112]
 Nedelcu  G,  Protesescu  L,  Yakunin  S,  Bodnarchuk  M  I, 
Grotevent M J, Kovalenko M V 2015 Nano Lett. 15 5635
[113]
 Liu  Z  H,  Cheng  P  P,  Li  Y  F,  Kang  R  Y,  Zhou  J,  Zhao  J,
Zuo Z Y 2022 Mater. Chem. Phys. 288 126393
[114]
 Bala A, Sen A, Shim J, Gandla S, Kim S 2023 ACS Nano 17
13784
[115]
 Chaudhary  M,  Yang  T  Y,  Chen  C  T,  Lai  P  C,  Hsu  Y  C,
Peng Y R, Kumar A, Lee C H, Chueh Y L  2023 Adv. Funct.
Mater. 33 2303697
[116]
 Tang B S, Veluri H, Li Y D, Yu Z G, Waqar M, Leong J F, 
Sivan  M,  Zamburg  E,  Zhang  Y  W,  Wang  J,  Thean  A  V  Y
2022 Nat. Commun. 13 3037
[117]
 Wang  X  J,  Zhou  Z,  Ban  C  Y,  Zhang  Z  P,  Ju  S,  Huang  X,
Mao H W, Chang Q, Yin Y H, Song M Y, Cheng S, Ding Y 
M, Liu Z D, Ju R L, Xie L L, Miao F, Liu J Q, Huang W 
2020 Adv. Sci. 7 1902864
[118]
 Chen J, Wang X J, Lu H, Liu Z D, Xiu F, Ban C Y, Zhou 
Z, Song M Y, Ju S, Chang Q, Liu J Q, Huang W  2018 Small
Methods 2 1800040
[119]
 Li Y J, Tang J S, Gao B, Sun W, Hua Q L, Zhang W B, Li 
X  Y,  Zhang  W  R,  Qian  H,  Wu  H  Q   2020  Adv.  Sci.  7
2002251
[120]
 Choi  S  H,  Park  S  O,  Seo  S,  Choi  S   2022  Sci.  Adv.  8
eabj7866
[121]
 Xu  W  T,  Min  S  Y,  Hwang  H,  Lee  T  W  2016  Sci. Adv.  2
e1501326
[122]
 Zhao Z, Abdelsamie A, Guo R, Shi S, Zhao J H, Lin W N, 
Sun  K  X,  Wang  J  J,  Wang  J  L,  Yan  X  B,  Chen  J  S  2021
[123]
物 理 学 报   Acta  Phys.  Sin .   Vol.  73, No.  20 (2024 )    207302 
207302-22

Nano Res. 15 2682
 Lv Z Y, Zhu S R, Wang Y, Ren Y Y, Luo M T, Wang H N, 
Zhang G H, Zhai Y B, Zhao S L, Zhou Y, Jiang M H, Leng 
Y B, Han S T 2024 Adv. Mater. 36 2405145
[124]
 Lv Z Y, Xing X C, Huang S M, Wang Y, Chen Z H, Gong 
Y, Zhou Y, Han S T 2021 Matter 4 1702
[125]
 Fu T, Liu X M, Gao H Y, Ward J E, Liu X R, Yin B, Wang
Z R, Zhuo Y, Walker D J, Joshua Yang J, Chen J H, Lovley 
D R, Yao J 2020 Nat. Commun. 11 1861
[126]
 Fu T, Liu X M, Fu S, Woodard T, Gao H Y, Lovley D R, 
Yao J 2021 Nat. Commun. 12 3351
[127]
 Matsukatova A N, Vdovichenko A Y, Patsaev T D, Forsh P 
A, Kashkarov P K, Demin V A, Emelyanov A V  2022 Nano
Res. 16 3207
[128]
 Yao  Z  Z,  Pan  L,  Liu  L  Z,  Zhang  J  D,  Lin  Q  J,  Ye  Y  X,
Zhang Z J, Xiang S C, Chen B L 2019 Sci. Adv. 5 eaaw4515
[129]
 Zhang B, Chen W L, Zeng J M, Fan F, Gu J W, Chen X H, 
Yan  L,  Xie  G  J,  Liu  S  Z,  Yan  Q,  Baik  S  J,  Zhang  Z  G,
Chen W H, Hou J, El-Khouly M E, Zhang Z, Liu G, Chen Y
2021 Nat. Commun. 12 1984
[130]
 Liu S Z, Zeng J M, Wu Z X, Hu H, Xu A, Huang X H, Chen
W  L,  Chen  Q  L,  Yu  Z,  Zhao  Y  Y  2023  Nat. Commun.  14
7655
[131]
 Liu Y, Zhou X F, Yan H, Shi X, Chen K, Zhou J Y, Meng J 
L, Wang T Y, Ai Y, Wu J X 2023 Adv. Mater. 35 2301321
[132]
 Yan X B, Zhao Q L, Chen A P, Zhao J H, Zhou Z Y, Wang 
J J, Wang H, Zhang L, Li X Y, Xiao Z, Wang K Y, Qin C 
Y, Wang G, Pei Y F, Li H, Ren D L, Chen J S, Liu Q  2019
Small 15 1901423
[133]
 Song Y G, Suh J M, Park J Y, Kim J E, Chun S Y, Kwon J 
U,  Lee  H,  Jang  H  W,  Kim  S,  Kang  C  Y  2021  Adv. Sci.  9
2103484
[134]
 Liu  Y  X,  Ye  C,  Chang  K  C,  Li  L,  Jiang  B,  Xia  C,  Liu  L,
Zhang X, Liu X Y, Xia T 2020 Small 16 2004619
[135]
 Kim  M  K,  Lee  J  S  2018  ACS  Appl.  Mater.  Interfaces  10
10280
[136]
 Wang  K  Y,  Chen  J  S,  Yan  X  B   2021  Nano  Energy  79
105453
[137]
 Li Y S, Xiong Y, Zhai B X, Yin L, Yu Y L, Wang H, He J 
2024 Sci. Adv. 10 eadk9474
[138]
 Jiang Y, Wang D C, Lin N, Shi S H, Zhang Y, Wang S C, 
Chen X, Chen H G, Lin Y A, Loong K C  2023 Adv. Sci. 10
2301323
[139]
 Yan X B, Zhao J H, Liu S, Zhou Z Y, Liu Q, Chen J S, Liu 
X Y 2017 Adv. Funct. Mater. 28 1705320
[140]
 Tang L Z, Wang J A, Huang Y, Wang H S, Wang C, Yang 
Y M 2024 J. Mater. Chem. C 12 3622
[141]
 Wang T, Wang M, Wang J W, Yang L, Ren X Y, Song G, 
Chen S S, Yuan Y H, Liu R Q, Pan L, Li Z, Leow W R, Luo
Y F, Ji S B, Cui Z Q, He K, Zhang F L, Lv F T, Tian Y Y, 
Cai K Y, Yang B W, Niu J Y, Zou H C, Liu S R, Xu G L, 
Fan X, Hu B H, Loh X J, Wang L H, Chen X D  2022 Nat.
Electron. 5 586
[142]
 Zhang Y C, Liu L, Tu B, Cui B, Guo J H, Zhao X, Wang J 
Y, Yan Y 2023 Nat. Commun. 14 247
[143]
 Zhang  G  H,  Xiong  Z  Y,  Gong  Y,  Zhu  Z  X,  Lv  Z  Y,  Wang
Y, Yang J Q, Xing X C, Wang Z P, Qin J R, Zhou Y, Han 
S T 2022 Adv. Funct. Mater. 32 2204721
[144]
 Liu  P  S,  Hui  F,  Aguirre  F,  Saiz  F,  Tian  L  L,  Han  T  T,
Zhang  Z  J,  Miranda  E,  Lanza  M   2022  Adv.  Mater.  34
2201197
[145]
 Zhang  Y,  Han  F,  Fan  S,  Zhang  Y  P  2021  ACS Biomater.
Sci. Eng. 7 3459
[146]
 Zhao M M, Wang S S, Li D W, Wang R, Li F F, Wu M Q, 
Liang K, Ren H H, Zheng X R, Guo C C, Ma X H, Zhu B 
W, Wang H, Hao Y 2022 Adv. Electron. Mater. 8 2101139
[147]
 Xia  Q,  Qin  Y  X,  Qiu  P  L  2022  Adv.  Electron.  Mater.  8
2200435
[148]
 Mullani N B, Kumbhar D D, Lee D H, Kwon M J, Cho S y, 
Oh  N,  Kim  E  T,  Dongale  T  D,  Nam  S  Y,  Park  J  H  2023
Adv. Funct. Mater. 33 2300343
[149]
 Han  J  S,  Le  Q  V,  Choi  J,  Hong  K,  Moon  C  W,  Kim  T  L,
Kim  H,  Kim  S  Y,  Jang  H  W  2018  Adv. Funct. Mater.   28
1870029
[150]
 Ye H B, Sun B, Wang Z Y, Liu Z Y, Zhang X N, Tan X H, 
Shi  T  L,  Tang  Z  R,  Liao  G  L  2020  J. Mater. Chem. C   8
14155
[151]
 Liu J Q, Gong J D, Wei H H, Li Y M, Wu H X, Jiang C P, 
Li Y L, Xu W T 2022 Nat. Commun. 13 7427
[152]
 Le  Corre  V  M,  Duijnstee  E  A,  El  Tambouli  O,  Ball  J  M,
Snaith H J, Lim J, Koster L J A  2021 ACS Energy Lett.  6
1087
[153]
 John  R  A,  Demira ğ Y,  Shynkarenko  Y,  Berezovska  Y, 
Ohannessian  N,  Payvand  M,  Zeng  P,  Bodnarchuk  M  I, 
Krumeich F, Kara G 2022 Nat. Commun. 13 2074
[154]
 Murdoch  B  J,  Raeber  T  J,  Zhao  Z  C,  McKenzie  D  R, 
McCulloch  D  G,  Partridge  J  G  2019  Appl. Phys. Lett.   114
2207928
[155]
 Li M J, Liu H F, Zhao R Y, Yang F S, Chen M R, Zhuo Y, 
Zhou C W, Wang H, Lin Y F, Yang J J  2023 Nat. Electron.
6 491
[156]
 Guo  J,  Wang  L  Y,  Liu  Y,  Zhao  Z  P,  Zhu  E  B,  Lin  Z  Y,
Wang P Q, Jia C C, Yang S X, Lee S J, Huang W, Huang 
Y, Duan X F 2020 Matter 2 965
[157]
 Mao J Y, Wu S, Ding G L, Wang Z P, Qian F S, Yang J Q, 
Zhou Y, Han S T 2022 Small 18 2106253
[158]
 Sun  L  F,  Zhang  Y  S,  Han  G,  Hwang  G,  Jiang  J  B,  Joo  B,
Watanabe K, Taniguchi T, Kim Y M, Yu W J, Kong B S, 
Zhao R, Yang H J 2019 Nat. Commun. 10 3161
[159]
 Wang  M,  Cai  S  H,  Pan  C,  Wang  C  Y,  Lian  X  J,  Zhuo  Y,
Xu K, Cao T J, Pan X Q, Wang B G, Liang S J, Yang J J, 
Wang P, Miao F 2018 Nat. Electron. 1 130
[160]
 Sun  Y  L,  Ding  Y  T,  Xie  D   2021  Adv.  Funct.  Mater.  31
2105625
[161]
 Khot A C, Nirmal K A, Dongale T D, Kim T G  2024 Small
20 2400791
[162]
 Bean B P 2007 Nat. Rev. Neurosci. 8 451[163]
 Wang Y, Gong Y, Huang S M, Xing X C, Lv Z Y, Wang J 
J,  Yang  J  Q,  Zhang  G  H,  Zhou  Y,  Han  S  T   2021  Nat.
Commun. 12 5979
[164]
 Wang  J  J,  Lv  Z  Y,  Xing  X  C,  Li  X  G,  Wang  Y,  Chen  M,
Pang  G  J,  Qian  F  S,  Zhou  Y,  Han  S  T  2020  Adv. Funct.
Mater. 30 1909114
[165]
 Zhong  Y  N,  Tang  J  S,  Li  X  Y,  Gao  B,  Qian  H,  Wu  H  Q
2021 Nat. Commun. 12 408
[166]
 Lamprecht R, LeDoux J 2004 Nat. Rev. Neurosci. 5 45[167]
 Wei H H, Shi R C, Sun L, Yu H Y, Gong J D, Liu C, Xu Z 
P, Ni Y, Xu J L, Xu W T 2021 Nat. Commun. 12 1068
[168]
 Tan H W, van Dijken S 2023 Nat. Commun. 14 2169[169]
 Zhao M R, Gao B, Tang J S, Qian H, Wu H Q  2020 Appl.
Phys. Rev. 7 011301
[170]
 Wang T Y, Meng J L, Rao M Y, He Z Y, Chen L, Zhu H, 
Sun  Q  Q,  Ding  S  J,  Bao  W  Z,  Zhou  P,  Zhang  D  W  2020
Nano Lett. 20 4111
[171]
 Upadhyay N K, Sun W, Lin P, Joshi S, Midya R, Zhang X 
M, Wang Z R, Jiang H, Yoon J H, Rao M Y, Chi M F, Xia 
[172]
物 理 学 报   Acta  Phys.  Sin .   Vol.  73, No.  20 (2024 )    207302 
207302-23

Q F, Yang J J 2020 Adv. Electron. Mater. 6 1901411
 Wong  H  S  P,  Raoux  S,  Kim  S,  Liang  J,  Reifenberg  J  P,
Rajendran  B,  Asheghi  M,  Goodson  K  E  2010  P.  IEEE  98
2201
[173]
 Chanthbouala  A,  Garcia  V,  Cherifi  R  O,  Bouzehouane  K,
Fusil S, Moya X, Xavier S, Yamada H, Deranlot C, Mathur 
N D, Bibes M, Barthélémy A, Grollier J 2012 Nat. Mater. 11
860
[174]
 Jung S, Lee H, Myung S, Kim H, Yoon S K, Kwon S W, Ju 
Y, Kim M, Yi W, Han S, Kwon B, Seo B, Lee K, Koh G H, 
Lee K, Song Y, Choi C, Ham D, Kim S J  2022 Nature 601
211
[175]
 Menzel  S,  Waters  M,  Marchewka  A,  Böttger  U,  Dittmann
R, Waser R 2011 Adv. Funct. Mater. 21 4487
[176]
 Ling H F, Tan K M, Fang Q Y, Xu X S, Chen H, Li W W, 
Liu Y F, Wang L Y, Yi M D, Huang R, Qian Y, Xie L H, 
Huang W 2017 Adv. Electron. Mater. 3 1600416
[177]
 Pei Y F, Li Z Q, Li B, Zhao Y, He H, Yan L, Li X Y, Wang 
J J, Zhao Z, Sun Y, Zhou Z Y, Zhao J H, Guo R, Chen J S, 
Yan X B 2022 Adv. Funct. Mater. 32 2203454
[178]
 Han J Q, Shan X Y, Lin Y, Tao Y, Zhao X N, Wang Z Q, 
Xu H Y, Liu Y C 2023 Small 19 2207928
[179]
 Hou W, Azizimanesh A, Dey A, Yang Y, Wang W, Shao C, 
Wu H, Askari H, Singh S, Wu S M 2024 Nat. Electron. 7 8
[180]
 Yin J, Zeng F, Wan Q, Li F, Sun Y M, Hu Y D, Liu J L, Li 
G Q, Pan F 2018 Adv. Funct. Mater. 28 1706927
[181]
 Xiao  T  P,  Bennett  C  H,  Feinberg  B,  Agarwal  S,  Marinella
M J 2020 Appl. Phys. Rev. 7 031301
[182]
物 理 学 报   Acta  Phys.  Sin .   Vol.  73, No.  20 (2024 )    207302 
207302-24

 
REVIEW
Recent progress of low-voltage memristor for
neuromorphic computing*
Gong Yi -Chun #    Ming Jian -Yu #    Wu Si -Qi     Yi Ming -Dong 
Xie Ling -Hai     Huang Wei     Ling Hai -Feng †
(State Key Laboratory of Organic Electronics and Information Displays, School of Materials Science and Engineering, Nanjing
University of Posts and Telecommunications, Nanjing 210023, China)
( Received 23 July 2024; revised manuscript received 30 August 2024 )
Abstract
Memristors  stand  out  as  the  most  promising  candidates  for  non-volatile  memory  and  neuromorphic
computing  due  to  their  unique  properties.  A  crucial  strategy  for  optimizing  memristor  performance  lies  in
voltage  modulation,  which  is  essential  for  achieving  ultra-low  power  consumption  in  the  nanowatt  range  and
ultra-low  energy  operation  below  the  femtojoule  level.  This  capability  is  pivotal  in  overcoming  the  power
consumption barrier and addressing the computational bottlenecks anticipated in the post-Moore era. However,
for  brain-inspired  computing  architectures  utilizing  high-density  integrated  memristor  arrays,  key  device
stability  parameters  must  be  considered,  including  the  on/off  ratio,  high-speed  response,  retention  time,  and
durability. Achieving efficient and stable ion/electron transport under low electric fields to develop low-voltage,
high-performance  memristors  operating  below  1  V  is  critical  for  advancing  energy-efficient  neuromorphic
computing  systems.  This  review  provides  a  comprehensive  overview  of  recent  advancements  in  low-voltage
memristors for neuromorphic computing. Firstly, it elucidates the mechanisms that control the operation of low-
voltage memristor, such as electrochemical metallization and anion migration. These mechanisms play a pivotal
role  in  determining  the  overall  performance  and  reliability  of  memristors  under  low-voltage  conditions.
Secondly, the review then systematically examines the advantages of various material systems employed in low-
voltage  memristors,  including  transition  metal  oxides,  two-dimensional  materials,  and  organic  materials.  Each
material system has distinct benefits, such as low ion activation energy, and appropriate defect density, which
are critical for optimizing memristor performance at low operating voltages. Thirdly, the review consolidates the
strategies for implementing low-voltage memristors through advanced materials engineering, doping engineering,
and  interface  engineering.  Moreover,  the  potential  applications  of  low-voltage  memristors  in  neuromorphic
function  simulation  and  neuromorphic  computing  are  discussed.  Finally,  the  current  problems  of  low-voltage
memristors  are  discussed,  especially  the  stability  issues  and  limited  application  scenarios.  Future  research
directions  are  proposed,  focusing  on  exploring  new  material  systems  and  physical  mechanisms  that  could  be
integrated into device design to achieve higher-performance low-voltage memristors.
Keywords: memristor, low-voltage, neuromorphic computing
PACS: 73.40.Rw, 81.07.–b, 85.35.–p, 07.05.Mh 　DOI: 10.7498/aps.73.20241022
CSTR ：32037.14.aps.73.20241022
 
*  Project  supported  by  the  National  Key  Research  and  Development  Program  of  China  (Grant  No.  2021YFA0717900),  the
National Natural Science Foundation of China (Grant Nos. 62288102, 22275098, 62471251), and the Postgraduate Research
& Practice Innovation Program of Jiangsu Province, China (Grant No. 46030CX21252).
#  These authors contributed equally.
†  Corresponding author. E-mail:  iamhfling@njupt.edu.cn 
物 理 学 报   Acta  Phys.  Sin .   Vol.  73, No.  20 (2024 )    207302 
207302-25

面向类脑计算的低电压忆阻器研究进展
贡以纯   明建宇   吴思齐   仪明东   解令海   黄维   凌海峰
Recent progress of low-voltage memristor for neuromorphic computing
Gong Yi-Chun      Ming Jian-Yu      Wu Si-Qi      Yi Ming-Dong      Xie Ling-Hai      Huang Wei      Ling Hai-Feng
引用信息 Citation: Acta Physica Sinica, 73, 207302 (2024)    DOI: 10.7498/aps.73.20241022
在线阅读 View online: https://doi.org/10.7498/aps.73.20241022
当期内容 View table of contents: http://wulixb.iphy.ac.cn
您可能感兴趣的其他文章
Articles you may be interested in
忆阻类脑计算
Memristive brain-like computing
物理学报. 2022, 71(14): 140501   https://doi.org/10.7498/aps.71.20220666
仿生生物感官的感存算一体化系统
Bio-inspired sensory systems with integrated capabilities of sensing, data storage, and processing
物理学报. 2022, 71(14): 148702   https://doi.org/10.7498/aps.71.20220281
蛋白质基忆阻器研究进展
Research progress of protein-based memristor
物理学报. 2020, 69(17): 178702   https://doi.org/10.7498/aps.69.20200617
基于忆阻器阵列的下一代储池计算
Next-generation reservoir computing based on memristor array
物理学报. 2022, 71(14): 140701   https://doi.org/10.7498/aps.71.20220082
面向感存算一体化的光电忆阻器件研究进展
Recent progress in optoelectronic memristive devices for in-sensor computing
物理学报. 2022, 71(14): 148701   https://doi.org/10.7498/aps.71.20220350
N型局部有源忆阻器的神经形态行为
Neuromorphic behaviors of N-type locally-active memristor
物理学报. 2022, 71(5): 050502   https://doi.org/10.7498/aps.71.20212017
