---
status: oa_fulltext
paper_name: "Letter Modeling Hyperspectral Response of Water-Stress Induced Lettuce Plants Using Artificial Neural Networks"
research_object: "water-stress induced lettuce plants"
original_paper_url: "Papers\\md\\Modeling_Hyperspectral_Response_of_Water.md"
resolved_doi: "10.1186/s12870-020-02807-4"
resolved_url: "https://doi.org/10.1186/s12870-020-02807-4"
oa_pdf: "https://bmcplantbiol.biomedcentral.com/track/pdf/10.1186/s12870-020-02807-4"
preprocessing_method: "removal of regions with a low signal-to-noise ratio (380 to 1020 nm), conversion of reflectance to absorbance using Beer–Lambert’s law"
feature_extracting_method: "hyperspectral wavelengths (reflectance and absorbance values)"
---

# Letter Modeling Hyperspectral Response of Water-Stress Induced Lettuce Plants Using Artificial Neural Networks

**Authors:** Anna Siedliska, Piotr Baranowski, Joanna Woźniak, Monika Zubik, Jaromir Krzyszczak

**Journal:** BMC Plant Biology

**Year:** 2021

## Abstract

BACKGROUND: Modern agriculture strives to sustainably manage fertilizer for both economic and environmental reasons. The monitoring of any nutritional (phosphorus, nitrogen, potassium) deficiency in growing plants is a challenge for precision farming technology. A study was carried out on three species of popular crops, celery (Apium graveolens L., cv. Neon), sugar beet (Beta vulgaris L., cv. Tapir) and strawberry (Fragaria × ananassa Duchesne, cv. Honeoye), fertilized with four different doses of phosphorus (P) to deliver data for non-invasive detection of P content. RESULTS: Data obtained via biochemical analysis of the chlorophyll and carotenoid contents in plant material showed that the strongest effect of P availability for plants was in the diverse total chlorophyll content in sugar beet and celery compared to that in strawberry, in which P affects a variety of carotenoid contents in leaves. The measurements performed using hyperspectral imaging, obtained in several different stages of plant development, were applied in a supervised classification experiment. A machine learning algorithm (Backpropagation Neural Network, Random Forest, Naive Bayes and Support Vector Machine) was developed to classify plants from four variants of P fertilization. The lowest prediction accuracy was obtained for the earliest measured stage of plant development. Statistical analyses showed correlations between leaf biochemical constituents, phosphorus fertilization and the mass of the leaf/roots of the plants. CONCLUSIONS: Obtained results demonstrate that hyperspectral imaging combined with artificial intelligence methods has potential for non-invasive detection of non-homogenous phosphorus fertilization on crop levels.

## Content

R E S E A R C H A R T I C L E Open Access
Identification of plant leaf phosphorus
content at different growth stages based
on hyperspectral reflectance
Anna Siedliska 1, Piotr Baranowski 1, Joanna Pastuszka-Wo źniak1, Monika Zubik 2 and Jaromir Krzyszczak 1*
Abstract
Background: Modern agriculture strives to sustainably manage fertilizer for both economic and environmental
reasons. The monitoring of any nutritional (phosphorus, nitrogen, potassium) deficiency in growing plants is a
challenge for precision farming technology. A study was carried out on three species of popular crops, celery
(Apium graveolens L., cv. Neon), sugar beet ( Beta vulgaris L., cv. Tapir) and strawberry ( Fragaria × ananassa
Duchesne, cv. Honeoye), fertilized with four different doses of phosphorus (P) to deliver data for non-invasive
detection of P content.
Results: Data obtained via biochemical analysis of the chlorophyll and carotenoid contents in plant material
showed that the strongest effect of P availability for plants was in the diverse total chlorophyll content in sugar
beet and celery compared to that in strawberry, in which P affects a variety of carotenoid contents in leaves. The
measurements performed using hyperspectral imaging, obtained in several different stages of plant development,
were applied in a supervised classification experiment. A machine learning algorithm (Backpropagation Neural
Network, Random Forest, Naive Bayes and Support Vector Machine) was developed to classify plants from four
variants of P fertilization. The lowest prediction accuracy was obtained for the earliest measured stage of plant
development. Statistical analyses showed correlations between leaf biochemical constituents, phosphorus
fertilization and the mass of the leaf/roots of the plants.
Conclusions: Obtained results demonstrate that hyperspectral imaging combined with artificial intelligence
methods has potential for non-invasive detection of non-homogenous phosphorus fertilization on crop levels.
Keywords: Hyperspectral imaging, Supervised classification, Phosphorus fertilization, Precision agriculture
Background
Phosphorus (P) is an essential macronutrient that greatly
influences root development, plant growth and crop
productivity [ 1]. Moreover, P has a significant function
in various metabolic processes in plants, such as protein
formation, photosynthesis, cell division, respiration,
energy storage and nutrient movement within the plant,
and is an integral constituent of nucleic acids,
phospholipids, and coenzymes activating amino acid
production [ 2]. P has been found to be one of the most
important minerals for celery ( Aqium graveolens )
growth, quality and yield. It was responsible for increas-
ing the total above-ground mass, marketable trimmed
yield and yield of larger grade sizes [ 3]. Phosphorus also
plays an important role in sugar beet development
because it is essential for root yield and sugar assimila-
tion [ 4, 5].
Inappropriate P fertilizer management is dangerous for
both plants and the environment and generates
additional costs. Fertilizers are commonly applied
© The Author(s). 2021 Open Access This article is licensed under a Creative Commons Attribution 4.0 International License,
which permits use, sharing, adaptation, distribution and reproduction in any medium or format, as long as you give
appropriate credit to the original author(s) and the source, provide a link to the Creative Commons licence, and indicate if
changes were made. The images or other third party material in this article are included in the article's Creative Commons
licence, unless indicated otherwise in a credit line to the material. If material is not included in the article's Creative Commons
licence and your intended use is not permitted by statutory regulation or exceeds the permitted use, you will need to obtain
permission directly from the copyright holder. To view a copy of this licence, visit http://creativecommons.org/licenses/by/4.0/.
The Creative Commons Public Domain Dedication waiver ( http://creativecommons.org/publicdomain/zero/1.0/) applies to the
data made available in this article, unless otherwise stated in a credit line to the data.
* Correspondence: j.krzyszczak@ipan.lublin.pl
1Institute of Agrophysics, Polish Academy of Sciences, ul. Do świadczalna 4,
20-290 Lublin, Poland
Full list of author information is available at the end of the article
Siedliska et al. BMC Plant Biology           (2021) 21:28 
https://doi.org/10.1186/s12870-020-02807-4

according to farmer experience, which can easily lead to
over- or misapplication, resulting in soil quality degrad-
ation, reduction in crop yields, contamination of the
environment, deterioration of water quality, eutrophica-
tion, and loss of biodiversity [ 6]. Therefore, adequate
phosphorus fertilization plays a key role in precision
agriculture. Currently, information about P status in
plants is obtained by visual inspection or chemical ana-
lyses, which are costly, time consuming and laborious.
Moreover, these methods are destructive, precluding
their usage for the continuous monitoring of P content
and thus P resources in the field during plant growth.
As a result, alternative and efficient methods of P con-
tent monitoring are needed in plants.
It is well known that phosphorus deficiency in plants
disturbs the production of chlorophyll, causing leaf chlor-
osis [ 7, 8]. Prolonged P deficiency may further result in
the accumulation of anthocyanins, consequently leading
to purple discolouration on the leaf surface [ 9, 10]. The
above-mentioned changes alter the spectral reflectance
characteristics of leaves or canopies and enable the appli-
cation of spectral reflectance methods, such as leaf colour
charts and chlorophyll metres, for the nondestructive esti-
mation of phosphorus status [ 11, 12]; however, most of
these methods focus on individual leaves. Hyperspectral
imaging, which combines spectroscopy with imaging
methods, allows collection of canopy images and delivers
representative reflectance data that are useful for the
determination of plant phosphorus status in the field. In
recent years, this technique has been effectively employed
for various crops to estimate biophysical parameters, such
as leaf area index [ 13, 14], leaf and fruit pigment content
[15– 21], biomass [ 22]a sw e l la sd e t e c t i o no fd i s e a s e sa n d
fungal infections [ 23– 26]. Several studies have been
reported on the spectral changes related to leaf water con-
tent [27, 28], chlorophyll content [29, 30]a n dm a c r o n u t r i -
ent content, e.g., nitrogen [31, 32] and potassium [ 33].
The objective of the automatic detection of nutri-
tional deficiencies is to identify the visual symptoms
that characterize such deficiencies. Most previous stud-
ies have focused on estimating the contents of bio-
chemical constituents in leaves as the response to
phosphorus deficiency of a single plant species, such as
citrus leaves [ 34, 35], rice [ 36], wheat [ 37], and oilseed
rape [ 6, 38]. Christensen et al. [ 39] indicated that P
content could be predicted with 74% accuracy based on
the spectral canopy reflectance. Similarly, high accuracy
(correlation coefficient of 0.710) has been obtained for
the determination of P content in oilseed rape leaves
using eight wavelengths selected from the visible and
near infrared (VIS-NIR) spectrum [ 6]. Mahajan et al.
[40] proposed the two-band (combination of 1080 nm
and 1460 nm wavelengths) vegetation index for the pre-
diction of P content in wheat. Most of these studies
have focused on the direct prediction of P content
based on reflectance indices combining a few spectral
bands or on indirect detection by predicting the con-
tent of a related substance (e.g., chlorophyll content).
Until now, few investigations have been dedicated to
analysing the temporal dynamics of leaf morphology
and colour under different P treatments covering lon-
ger periods of plant growth and development and mul-
tiple bands of visible/infrared spectrum [ 41, 42].
It is evident from previous studies that the monitoring
of P status in different crops using hyperspectral systems
is possible; however, more attention should be paid to
properly characterize plant spectral response to varied P
fertilization, including the key stages of growth. More-
over, to our knowledge, there is still insufficient effort
dedicated to the classification of nutritional anomalies in
root vegetables (such as wild celery - Apium graveolens
L.). These limitations have become the prerequisites for
undertaking research to develop robust and more spe-
cific algorithms for predicting P status in plants (includ-
ing root vegetables) at different development stages and
fertilization doses.
The aim of the present study was to develop a discrim-
ination model for monitoring the dynamics of plant
phosphorus (P) status across the different developmental
stages of wild celery, strawberry and sugar beet crops
under different P fertilizations using hyperspectral
reflectance measurements. The three species selected for
this study are very popular in temperate climatic zones
due to the economic importance (sugar beet is the main
source of sugar in many countries), as well as their
nutritional value and taste (celery and strawberry).
Results and discussion
Reference data of chlorophyll and macronutrient content
Different P treatments caused major variations in pig-
ment content in all the studied plants. Figure 1 illus-
trates the contents of Chlorophyll a , Chlorophyll b , Total
chlorophyll and Carotenoids in sugar beet, celery and
strawberry plants in response to different P fertilizations.
The results show that, in the case of sugar beet and
strawberry plants, exceeding the recommended dose of
phosphorus in the nutrient solution (yellow bars in Fig. 1
depicting a 33% increase of P) caused a decrease in the
chlorophyll content, which refers to all the measured
kinds of chlorophyll (Chlorophyll a , Chlorophyll b and
Total chlorophyll). The same trend was observed in cel-
ery plants, but to a smaller extent. For the three studied
species, the maximum chlorophyll concentrations were
recorded for various P doses: for sugar beet, the dose
was under 33% of the recommended dose, for celery,
under 67% of the recommended dose and, for straw-
berry, under the recommended dose. These differences
speak to the varying impacts of P on the chlorophyll
Siedliska et al. BMC Plant Biology           (2021) 21:28 Page 2 of 17

activity of various species. The deficiency or excessive
application of P into the growing pots caused very high
decreases in chlorophyll and carotenoid concentrations
only in strawberry leaves compared to the control group
(those with the recommended dose), which can be
related to leaf chlorosis. This result indicates a high sen-
sitivity of strawberry plants to imbalanced phosphorus
dosing, in agreement with observations of Trejo-Téllez
and Gómez-Merino [ 43], who noticed a considerable
decrease of chlorophyll content in P-deficient strawberry
leaves, which became uniformly yellow under P stress.
Additionally, Estrada-Ortiz et al. [ 44] confirmed a strong
relationship between P content in strawberry plants and
the accumulation chlorophylls in its leaves. Moreover,
Fig. 1 Measured content of Chlorophyll a, Chlorophyll b, total Chlorophyll and Carotenoids in sugar beet ( a), celery ( b) and strawberry ( c) plants
under different P applications. Bars followed by the same letter do not differ statistically by Tukey ’s test at p=0.05
Siedliska et al. BMC Plant Biology           (2021) 21:28 Page 3 of 17

these authors indicated that excess P application causes
a decrease in the contents of photosynthetic pigments
and also influences serious soil and environmental deg-
radation. Figure 1 shows that the concentrations of
chlorophyll a in the studied species were much higher
than the concentrations of chlorophyll b. This result is
not in agreement with Costa et al. [ 45], who observed
that Chlorophyll b concentrations were higher than
Chlorophyll a in 2 cultivars of strawberry under varied
lightening conditions. However, it was previously indi-
cated that the relationship between chlorophyll a and b
depends on many factors, including source of light,
shading, ambient conditions of plant growth [ 46– 48]
and the specific role of these two pigments in plant
physico-chemistry. Chlorophyll a is responsible for
the collection of photons and plays an essential role
in photosynthesis, while ch lorophyll b additionally
participates in the transference of light radioactive
energy [ 49, 50].
In celery leaves, the chlorophyll concentration (for all
3 types of chlorophyll) at the lowest P treatment (P-33)
was much lower than in other P treatments, indicating
that such low P supply has a stress effect on celery. For
celery leaves, the highest values of chlorophyll concen-
tration occurred for the variant P-67, not P-100, which
speaks to the overestimation of the recommended P
dose in the fertilizer in this case. The same was noticed
for the carotenoid content in celery leaves (the highest
value was noticed for the P-67 variant). It was also ob-
served in celery plants that the highest dose of P in
fertilizer (P-133 variant) did not lead to such high
decreases in chlorophyll a, b or total concentrations, as
was the case for the lowest fertilizer dose (variant P-33),
which suggests that celery is more sensitive to the scar-
city of P than to its excess.
The total N, P, K, Mg and Ca contents, measured by
reference methods at 49, 51 and 45 DAT for celery,
sugar beet and strawberry plants, are shown in Fig. 2.
Generally, considerable and statistically significant differ-
ences in macronutrient contents were observed between
various P treatments in the studied species. However,
neither foliar P concentrations in the sugar beet and cel-
ery plants nor Mg concentrations in celery and straw-
berry were significantly affected by P treatment. It was
difficult to find strict tendency in macronutrient content
changes in the leaves of the three studied species with
changing P fertilization. For example, in sugar beet and
celery, the lowest dose of P in fertilizer (P-33) led to the
highest values of N, which could be due to specific inter-
actions between nutrient elements in the substrate, as
explained in research conducted by Y. Li et al. [ 3]. Simi-
larly, the lowest dose of P in fertilizer (P-33) was
reflected in the highest concentrations of K for each of
the species. The highest contents of Ca were observed in
celery leaves; however, increasing trends with rising P
concentrations in the treatments were not confirmed in
sugar beet or strawberry. These results confirm the com-
plicated relationships between the contents of macronu-
trients in leaves and P treatments in the soil, which was
also suggested in other sources [ 3, 51, 52].
Correlation between leaf biochemical constituents,
phosphorus fertilization and mass of the leaf/roots of the
plants
Pearson correlation coefficients (PCC) between the leaf
macronutrients (N, P, K, Ca, Mg), total chlorophyll
(Chltot), carotenoids (Car), phosphorus fertilization level
(Psuppl), mass of the leaf (m leaf) and mass of root (m root)
for the studied species are presented in Fig. 3 as correl-
ation matrices. The leaf pigments and nutritional ele-
ments were evaluated through laboratory analysis at the
end of the experiment. All plants showed a negative cor-
relation between the level of P supply and the concentra-
tion of nitrogen (N) and potassium (K) macronutrients.
The results obtained for celery showed a strong positive
correlation (PCC=0.77) between the applied dosed of
phosphorus fertilizer and the calcium content in plant
leaves, whereas the other plants indicated a negative cor-
relation (PCC=-0.81 for sugar beet and PCC=-0.69 for
strawberry). Earlier reports also indicated a strong phos-
phorus fertilization effect on other macronutrient accu-
mulation in plants [ 53, 54].
A negative and highly significant correlation was
observed between the level of P supplementation and
chlorophyll concentration in sugar beet, while the
other plants showed non-significant correlations. The
applied fertilization had no strong effect on the con-
centrations of carotenoids in plant leaves. Phosphorus
fertilization was positively c orrelated with the concen-
tration of this element in plant leaves, especially cel-
ery (PCC=0.70) and strawberry plants (PCC=0.70).
Sugar beet showed a smaller correlation between the
level of P supplementation and P content in plant
leaves. This dependence is consistent with some ob-
servations in previous studies indicating that P
fertilization increases the phosphate content of sugar
beet roots [ 55]. Most of the plant nutritional elements
were highly correlated with each other. Numerous
significant correlations existed between nutrients in
sugar beet, especially between K and Ca (PCC=0.88)
a n dNa n dM g( P C C = 0 . 8 2 ) .T h es t r o n gc o r r e l a t i o n s
between chlorophyll content and carotenoids were ob-
served for celery (PCC=0.85) and strawberry (PCC=
0.95) plants. This is because chlorophylls and caroten-
oids are co-varying in nature (as a components of
photosynthetic antenna complexes) and statistically
dependent, as observed in previous studies [ 16, 56].
Siedliska et al. BMC Plant Biology           (2021) 21:28 Page 4 of 17

Negative correlations between P supplementation in soil
and mass of the plant roots suggest that P deficiency pro-
motes a reduction in the mass and length of roots in root
vegetables and causes the reduction in yield. In the case of
strawberry, this correlation was positive. The concentra-
tion of chlorophylls and carotenoids in the above-ground
parts of the tested plants significantly affected the mass of
their roots. Sugar beet had a positive correlation between
the carotenoid content and root mass (PCC = 0.6),
whereas a strong negative correlation was observed
between the concentration of chlorophyll and carotenoid
content in leaves and root mass for celery plants.
Fig. 2 Effect of phosphorus treatment on N, P, K, Ca and Mg in leaf samples determined by traditional methods. Bars followed by the same letter
are not significantly different according to Tukey ’s test ( p< 0.05)
Siedliska et al. BMC Plant Biology           (2021) 21:28 Page 5 of 17

Spectral features of plants
Figure 4 represents the general scheme of the proced-
ure to obtain spectral characteristics from the leaf
surfaces of the three studied plants. The average
reflectance spectra of ROIs, covering the spectral
range of 400 – 2500 nm for leaf samples of the three
studied species of plants with different P treatments
and for five development stages, are shown in Fig. 5.
The spectral curves of the leaves of the three studied
species exhibited similar shapes, although differences
are visible between the spectra belonging to specific
variants. In the visible spectral region, a characteristic
peak was observed at 550 nm with some differences
between variants, especially in sugar beet and straw-
berry. This peak is characteristic of chlorophyll
absorption. In the region of rapid change in the
reflectance of vegetation in the near infrared range of
650– 750 nm of the electromagnetic spectrum (so
called red edge), high increases of reflectance occur,
which enabled us to distinguish differences between
some variants of the experiments. The highest differ-
entiation between the spectral curves of the plants
belonging to specific variants was observed in the
range of 750 – 1300 nm, in which reflectance patterns
are strongly connected with the internal cellular
structure of plants [ 57]. Unfortunately, in this range,
there was a break (discontinuity) in the registered
reflected radiation, which is connected to low sensi-
tivity of the two spectral cameras used in the part of
this range. Because of this, the raw spectra of the
leaves in this range were not good at distinguishing
between variants. Another part of the spectrum that
seems to be appropriate for distinguishing differences
between variants is absorption at approximately 1400
and 1950 nm, which are highly related to the absorp-
tion by water. The results presented in Fig. 5 indicate
quantitative relationships between the amount of
reflected light and P treatment at the succeeding
growing stages. In plants of all three species, the
highest changes in reflectance values were observed in
the SWIR region (2200 – 2400 nm). It suggests that the
SWIR region is useful for distinguishing levels of P
fertilization. Wavelengths in the SWIR region are
mainly associated with light absorption by proteins,
nitrogen, cellulose, starch and sugar. It is known that
P plays an important role in protein synthesis, which
may explain these differences, as suggested by Knox
et al. [ 58].
Fig. 3 Correlations between carotenoids (Car), chlorophyll (Chl tot), magnesium (Mg), calcium (Ca), potassium (K), phosphorus (P), nitrogen (N)
content in leaf, leaf mass (mleaf), root mass (mroot) and phosphorus supplementation (P suppl)
Siedliska et al. BMC Plant Biology           (2021) 21:28 Page 6 of 17

Effective wavelength selection
To reduce the high dimensionality of the extracted spec-
tral data and to make the classification models more
robust, the most appropriate wavelengths that give the
highest discrimination among different levels of P-
treatment were selected based on 2nd derivative trans-
formation of raw spectra. The 2nd derivative averaged
spectra are shown in Fig. 6. Based on the second deriva-
tive transformation of the original spectra and by apply-
ing the CFS algorithm with greedy stepwise selection
method, 10, 7 and 4 wavelengths were selected for classi-
fication according to the P treatment of sugar beet,
celery and strawberry plants, respectively (Table 1). The
wavelengths used to distinguish between levels of P
fertilization were localized in the blue spectral band
(400– 480 nm), NIR (760 – 900 nm) and SWIR (1000 –
2500 nm) regions of the spectrum. In all studied plants,
the level of P supply did not significantly affect the
reflectance in the green (500 – 560 nm) region. In the
case of strawberry plants, the wavelengths from the red
region (715 and 723 nm) and SWIR region (2301 and
2332 nm) had particular importance for the separation
of the levels of P treatment. The wavelengths in the red
and far-red regions of the electromagnetic spectrum
(723, 754, 715 and 723 nm) in plants are mainly associ-
ated with the absorption of Chlorophyll a. It was shown
that varied P rates cause changes in the concentration of
Chlorophyll a in plant leaves (Fig. 1).
The previous study performed by Osborne et al. [ 9]
also indicated that NIR (730 nm and 930 nm) and blue
(440 and 445 nm) regions of the spectrum are useful for
the prediction of P concentrations in corn canopy. Dif-
ferences in the selected wavelengths among the three
studied species might be due to differences in plant
structure or changes in the chemical concentration.
Results of discrimination analysis
The prediction accuracies of the models created to dis-
tinguish between plants grown under different levels of
P treatment at different development stages obtained for
the three studied plant species are presented in Table 2.
It results from the analysis of the supervised classifica-
tion algorithms that very similar and relatively high pre-
diction accuracies in the majority of cases (ranging from
40 to 100% for validation sets) were obtained for all four
methods of machine learning model creation methods
Fig. 4 General scheme of the procedure to generate spectral characteristics from hyperspectral images of the three studied plants
Siedliska et al. BMC Plant Biology           (2021) 21:28 Page 7 of 17

(i.e., backpropagation neural network, random forest,
naive Bayes and support vector machines). In all cases,
despite very limited numbers of wavelengths selected for
the classification (from 4 to 10), the prediction accur-
acies for training sets were very high in all variants of
the experiment. This confirms a good performance of
the CFS wavelength selection algorithm and is in agree-
ment with other studies on plant material classification
with the use of this algorithm [ 26, 59]. The performance
of the validation sets was considerably lower than that of
the training sets, but the accuracy at distinguishing be-
tween various levels of P treatment were equal or higher
than 80% in 11 variants among 15 variants of species/
stages of plant development. This result is very good al-
though difficult to compare with other studies that used
different experimental setups and limited numbers of P
treatment variants [ 38, 42]. The lowest percentages of
correctly classified instances were obtained for the first
Fig. 5 Average reflectance spectra of sugar beet ( a), celery ( b) and strawberry plants ( c) grown under different phosphorus (P) fertilization rates
obtained for third development stage. Each line correspond to the spectral characteristics averaged for four plants from each variants of
the experiment
Siedliska et al. BMC Plant Biology           (2021) 21:28 Page 8 of 17

Fig. 6 Second derivative transformed spectra of sugar beet ( a), celery ( b) and strawberry plants ( c) grown under different phosphorus (P)
fertilization rates obtained for third development stage
Table 1 Wavelengths selected based on the second derivative transformed spectra and CFS algorithm with greedy-stepwise
selection methods
Plant species Number of selected wavelengths Selected wavelengths [nm]
Sugar beet 10 422, 569, 723, 850, 1250, 2227, 2276, 2314, 2345, 2351
Celery 7 414, 419, 429, 564, 754, 1395, 2264
Strawberry 4 715, 723, 2301, 2332
Siedliska et al. BMC Plant Biology           (2021) 21:28 Page 9 of 17

stage of plant development; however, with progress in
the development of plants, this accuracy was higher.
This result comes from the fact that, in the first period
of plant development, the changes in leaf spectral prop-
erties are considerably minimal between various P treat-
ments and misclassification, especially with one level or
higher of P fertilization. Although all four methods of
supervised classification model creation were highly ef-
fective, the highest overall classification performance
was obtained for RF models. The validation results indi-
cated that this model correctly classified more than 70%
of all instances in the case of strawberry plants and more
than 80% (except the second term) for celery across five
development stages. The average accuracy of RF classifi-
cation for sugar beet was lower compared to other
plants (65%). This result might be explained by the spe-
cific nutrient requirements of the sugar beet [ 55, 60] and
its lower sensitivity of imbalanced P-fertilization than
strawberry and celery plants.
To assess the performance of the analysed models
for specific P levels in five developmental stages, con-
fusion matrices were created, which enabled us to
identify misclassification percentages for analysed vari-
ants of the experiment. The summary of this analysis
is presented in Table 3 for RF models, which gave
the best overall results in the performed experiments.
The grey cells in this table represent variants with
100% accuracy (all cases clas sified correctly), yellow
cells show misclassified variants in which misclassifi-
cation refers to one level up or down with respect to
the analysed P fertilization level (e.g., P-33 level clas-
sified as P-67 level), and red cells indicate misclassifi-
cation higher than one P fertilization level (e.g.,
variant P-133 classified as P-33). The confusion matri-
ces for all models divided to 5 growth stages are pre-
sented in Table S 1 in Supplement 1. For each
developmental stage, the percentages of misclassified
cases are given, and it is possible to see how mis-
classification occurred (second column in this table
indicates the analysed variants, and separate rows
show with which variants they were misclassified and
what percent of misclassification occurred). From this
table, 100% accuracy was achieved (all cases classified
correctly) for 26 variants of the experiment (P level
vs development stage), misclassification was one level
up or down with respect to the analysed P
fertilization level in 27 variants, and misclassification
was higher than one P fertilization level in only 13
variants. In the majority of misclassified variants (26),
improperly classified cases reached only 20%, there
Table 2 Model performance on selected wavelengths for classification of the level of P treatment at five developmental stages
obtained for the three studied species of plants
Plant species Sugar beet Celery Strawberry
Model BNN LIBSVM LOG RF BNN LIBSVM LOG RF BNN LIBSVM LOG RF
I Training set % 98 84 91 100 98 91 100 100 86 79 68 100
RMSE 0.12 0.28 0.18 0.15 0.12 0.21 0 0.12 0.19 0.32 0.31 0.1
Validation set % 55 45 50 65 75 60 80 80 80 60 55 70
RMSE 0.44 0.52 0.49 0.35 0.3 0.45 0.32 0.32 0.29 0.45 0.39 0.29
II Training set % 98 89 100 100 98 93 95 100 97 97 100 100
RMSE 0.11 0.24 0 0.11 0.12 0.18 0.17 0.13 0.09 0.11 0 0.05
Validation set % 70 70 65 70 55 60 50 55 80 90 80 95
RMSE 0.37 0.39 0.42 0.29 0.39 0.45 0.48 0.34 0.26 0.22 0.31 0.16
III Training set % 95 86 100 100 100 91 100 100 98 77 82 100
RMSE 0.13 0.26 0 0.12 0.06 0.22 0.01 0.11 0.15 0.34 0.22 0.09
Validation set % 65 60 40 75 80 95 55 80 100 85 80 95
RMSE 0.23 0.45 0.55 0.33 0.29 0.16 0.47 0.28 0.17 0.27 0.24 0.15
IV Training set % 100 93 100 100 100 97 100 100 100 100 100 100
RMSE 0.07 0.19 0 0.11 0.05 0.11 0 0 0.02 0 0 0.01
Validation set % 55 85 55 90 80 75 65 85 100 100 95 100
RMSE 0.38 0.27 0.47 0.27 0.27 0.35 0.41 0.27 0.03 0 0.14 0.05
V Training set % 87 86 100 100 100 95 100 100 91 86 100 100
RMSE 0.21 0.26 0 0.13 0.03 0.15 0 0 0.2 0.26 0 0.11
Validation set % 60 45 65 70 95 95 90 95 65 50 80 80
RMSE 0.37 0.52 0.41 0.35 0.15 0.16 0.22 0.16 0.34 0.5 0.32 0.3
Siedliska et al. BMC Plant Biology           (2021) 21:28 Page 10 of 17

were only 9 variants with misclassified cases of 40%,
3 variants with misclassified cases of 60% and 1 vari-
ant with misclassified cases of 80%. Table 3 also
shows that there were only 6 variants for which two
different levels of P treatment were assigned for a
given level, five of which occurred for the first and
second plant developmental stages. In Fig. 7,t h e
numbers of misclassified cases in the validation data-
set for random forest (RF) models of P content in
plant treatment for 5 stages of plant growth and 3
studied species are presented, and these are based on
the confusion matrices presented in Table S 1 in Sup-
plement 1. This figure shows that the highest number
of misclassified cases for sugar beet and strawberry
occurred during the first stage of plant growth,
whereas this occurred du ring the second stage of
plant growth for celery. This confirms that, in the
early stages of plant growth, spectral properties of the
affected plant leaves do not always distinguish differ-
ences in P content. Despite this, the overall classifica-
tion performance of the chosen models (and
especially RF models) was very good.
Conclusions
There is high potential of hyperspectral screening for
controlling adequate phosphorous nutrition of culti-
vated plants, which is vital for creating proper condi-
tions of their production and responses to
environmental factors. The experiment conducted on
sugar beet, celery and strawberry indicated that it is
possible for these species to distinguish, with high ac-
curacy, the differences in ph osphorous nutrition using
machine learning modelling on the basis of second
derivatives of the reflectance spectra in the spectral
Table 3 Summary of confusion matrices created for the random forest (RF) models of the phosphorous content in treatments for
the three studied species (sugar beet, celery and strawberry) at five stages of plant growth
m.a means “misclassified as ” - name of a variant to which a given variant was assigned during the classification
% - percent of misclassified cases belonging to a given variant
The grey cells - all cases classified correctly; yellow cells - one level up or down misclassified variants with respect to the analysed P fertilizatio n level; red cells -
misclassification higher than one P fertilization level
Siedliska et al. BMC Plant Biology           (2021) 21:28 Page 11 of 17

region of 450 – 2500 nm. Moreover, it elaborated that
procedures provide a chance to distinguish different
levels of phosphorus fertilization at different develop-
mental stages of plants. Phosphorus deficiency can be
accurately classified at an early plant developmental
stage, especially for celer y and strawberry; however,
the classification accuracy increases during plant
growth.
The results have several practical implications. First,
they can be applied to the fast and non-destructive ana-
lysis of phosphorous availability for the examined three
species as an element of precision farming. In particular,
the detection of insufficiencies in P content is possible
with multispectral scanners installed on tractor plat-
forms supported with GPS systems, through implement-
ing selected spectral bands into available sensors, and
through direct use of the elaborated procedures of data
analysis and supervised classification. The method en-
ables us to pin-point areas in the cultivated fields or
even individual plants requiring attention. In this con-
text, it is especially important that elaborated models
concern different stages of plant growth, which is an
additional advantage of such screening. The second pos-
sible application of the study is its implementation to
unmanned aerial vehicles that are capable of distant ana-
lysis of large areas at a time. However, some additional
technical aspects should be considered in such systems,
such as irregular lightening of the analysed scene, the
occurrence of strong vibrations, and controlling flight
trajectories.
The authors are aware that further studies are
needed to explore the impact of soil type on accumu-
lated phosphorous in plants, interactions between
phosphorous status in plants frequently undergoing
abiotic and biotic stresses and their representation in
reflectance spectra and chemometric analysis. Such
additional studies will strengthen the performance of
the elaborated method in detecting phosphorous sta-
tus in plants.
Methods
Plant material
The same number of plants of three species was used
for the experiment: 64 celery ( Apium graveolens L., cv.
Neon), 64 sugar beet ( Beta vulgaris L., cv. Tapir) and 64
strawberry ( Fragaria × ananassa Duchesne, cv. Hon-
eoye). The seeds of celery (produced by SEMO) and
sugar beet (produced by SESVanderHave) were pur-
chased commercially, while the strawberry seedlings
with qualification certificate were obtained from Li-
censed Strawberry Nursey (Niewczas Krystyna & Józef,
Wielowicz 31, 89 – 412 So śno, Poland). On March 2018,
seeds of celery ( Apium graveolens L., cv. Neon) and
sugar beet ( Beta vulgaris L., cv. Tapir) were sown in
plastic pots containing peat. After germination, seedlings
of similar sizes were transplanted to pots (one seedling
per pot) containing sand. The seedlings of strawberry
plants were directly placed in pots with sand. The plants
were grown in the greenhouse under natural sunlight
supplemented white LED light at light intensity of
320 μmol m− 2 s− 1 using a photoperiod of day/night set
to 12/12 h, with temperature ranging from 20 °C to 22 °C
during the months of March – June and September and
from 24 °C to 26 °C during the months of July – August.
Treatments
In this experiment, the plants from each species were
divided equally into four groups of 16 plants each and
were subjected to four different phosphorus rates, which
were applied to the pots to stimulate different nutrient
Fig. 7 Numbers of misclassified cases in a validation dataset for random forest (RF) models of P content in plant treatment for 5 stages of plant
growth and 3 studied species
Siedliska et al. BMC Plant Biology           (2021) 21:28 Page 12 of 17

levels in plant leaves to test the hyperspectral imaging
system. P fertilizer in the form of superphosphate (P 2O5)
was applied to the pots directly before seedling in vari-
ous quantities to obtain different fertilization schemes
named P-33%, P-67%, P-100%, and P-133%. In the vari-
ant P-100%, which was the control group for the whole
experiment, the dose recommended in the literature for
these types of varieties was used [ 61– 63], namely 1.2 g P
per pot (40 mg/kg of the soil). Other variants were
treated with 1/3, 2/3, and 4/3 of this value. After initial
differentiation, each plant was irrigated with 100 ml of
the treatment solution every two days for 60 days. The
nutrient solution contained 33.3 mg/l of N, 13.3 mg/l of
P and 50 mg/l of K applied as NH 4NO3, Ca(H 2PO4)2
and KNO 3, respectively. The concentrations of micronu-
trients were B 0.28, Fe 2.4, Mn 1.0, Zn 0.35, and Mo
0.05 mg/l, which were applied as a commercial fertilizer
Micro Plus (produced by Intermag, Olkusz, Poland).
After 60 days, a constant level of the soil water content
was maintained in pots corresponding to the field cap-
acity of water. To do so, the field capacity of water for
the used soil was determined for selected soil samples
under the soil water potential of 15,596 J·m − 3 (pF equal
to 2.2) in the Richard ’ s chambers (Soilmoisture Equip-
ment Corp., Santa Barbara, CA, USA). At that stage, the
plants were watered using tap water, and the appropriate
soil water content was controlled using a weighting
method.
Hyperspectral imaging system
Spectral data were recorded by a laboratory hyper-
spectral imaging system, which was composed of two
hyperspectral cameras manufactured by SPECIM
(Spectral Imaging Ltd., Oulu, Finland) to cover the
ranges of visible and near-infrared (VNIR) and short-
wavelength infrared (SWIR), a belt conveyor (Reall,
Lublin, Poland) with belt speed regulated for each
camera separately (to conduct line scanning of the
plant leaves) and the illumination system Brilum
(Piaseczno, Poland) model LAVADO416 with 4 light-
ing modules (each of them had 4x20W halogen lamps
made by Philips, the Netherlands). The following im-
aging spectrographs were used inside the hyperspec-
tral cameras: ImSpector V10E (400 – 1000 nm) and
N25E 2/3 ″ imaging spectrometer (1000 – 2500 nm).
The constant distance of 20 cm between the lenses of
the cameras and the plant surfaces were maintained
for each scan. The angle between the halogen lamps
frames and the conveyor belt surface was 45°.
Image acquisition and correction
The three-dimensional hyperspectral data, composed of
960 images of the plants (4 nutrient treatment × 5 devel-
opment stages × 16 replications × 3 species of plants),
were collected before chemometric analysis, and super-
vised classification were performed. Plants were scanned
with the hyperspectral camera when staying in pots with-
out uprooting. Data collection was performed five times
during the experiment under differing stages of plant de-
velopment, numbered as 1, 2, 3, 4 and 5. They represented
7, 14, 21, 35 and 49 days after transplanting (DAT) for cel-
ery plants; 7, 21, 31, 41 and 51 DAT for sugar beet plants;
and 7, 14, 21, 35 and 45 DAT for strawberry plants. De-
scription of development stages achieved by each plant
species along with the code assigned on BBCH scale is
provided in Table 4. For three studied species they cov-
ered the broad period from the unfolding of the second
leaf till the appearance of the first fruit.
Hyperspectral images were recorded at a wavelength
range of 400 – 1000 nm with a spectral resolution of 2.8
nm using a VNIR camera and in the range of 1000 – 2500
nm with a spectral resolution of 10 nm using a SWIR
camera. During image acquisition, the plant samples were
placed on the mobile platform using the scanning speed
of 6 mm/s and 8 mm/s, and the camera exposure time was
set to 2.3 and 7.6 ms for the VNIR and SWIR cameras, re-
spectively. The hyperspectral images obtained during the
measurements were recorded using data acquisition
Table 4 The description of measurement dates based on BBCH (Biologische Bundesanstalt, Bundessortenamnt and Chemische
Industrie) development stages [ 64, 65]
Measurement
term
Plant species
Sugar beet Celery Strawberry
BBCH
Code
Description BBCH
Code
Description BBCH
Code
Description
I 12 2nd true leaf unfolded 12 2nd true leaf unfolded 12 2nd true leaf unfolded
II 15 5th true leaf unfolded 14 4th true leaf unfolded 14 4th true leaf unfolded
III 19 9 or more true leaves
unfolded
19 9 or more true leaves unfolded 58 Early balloon stage: first flowers with petals
forming a hollow ball
IV 32 Leaves cover 20% of
ground
42 20% of the expected root
diameter reached
65 Full flowering: 50% of flowers open
V 35 Leaves cover 50% of
ground
45 50% of the expected root
diameter reached
85 First fruits have cultivar-specific colour
Siedliska et al. BMC Plant Biology           (2021) 21:28 Page 13 of 17

software SpectralDAQ ver. 2.1, which is specially dedi-
cated to SPECIM cameras. For each series of measure-
ments, white and dark calibrations were performed
according to the procedure described in Baranowski et al.
[24] to obtain the reflectance from the raw data.
Hyperspectral image pretreatment
The corrected images were used to extract spectral in-
formation, select effective wavelengths, and elaborate the
method of identification of P content in plants. First, the
regions of interest (ROIs), including leaf surfaces, were
pinpointed via ENVI software (ENVI5.4, Research Sys-
tem Inc., Boulder, CO, USA). Next, segmentation was
implemented to segregate the ROIs. The segmentation
was performed according to the procedure described by
Baranowski et al. [ 59]. After image segmentation, reflect-
ance values of all the pixels in each separate ROI were
averaged to generate one mean value for each band.
That way, the mean values of reflectance from 434 bands
produced the representative reflectance spectrum of
each sample. This procedure is referenced in the
manuscript as the averaging of the reflectance spec-
tra. Before the classificat ion analysis, the extracted
spectra were preprocessed using the second deriva-
tive, calculated with the Savitzky-Golay (SG) method
(second-order polynomial and 11 smoothing points).
The derivative processing suppresses the background
signal as well as reduces image artefacts caused by
non-uniform illumination [ 66]. Moreover, this pre-
processing method increases the spectral resolution,
has an input in the baseline correction, and enables
an increased resolution of overlapping peaks [ 32].
Spectra obtained with the use of this preprocessing
method are referenced in the manuscript as second
derivative transformed s pectra. The Unscrambler X
ver. 10.1 (CAMO Software, Oslo, Norway) was used
to pre-treat the spectral data.
Effective wavelength selection
Hyperspectral image data contain large amounts of in-
formation, with redundancy and multi-collinearity be-
tween adjacent wavelengths, causing complex problems
with their processing and application. To solve these
problems, it is necessary to extract a number of essential
wavelengths carrying the most relevant information be-
fore further analysis and implementation. To reduce the
high dimensionality of the spectral data, the Correlation-
Based Feature Selection (CFS) algorithm was applied to
the SG transformed data. This algorithm uses heuristics
that assign high scores to feature subsets that are highly
correlated with the class and highly uncorrelated with
each other [ 67]. In this research, a greedy-stepwise (GS)
search strategy was applied in the CFS algorithm to se-
lect attributes through the space of subsets.
Classification algorithms
Supervised classification experiments were performed on
the hyperspectral data of the plant leaves. Different
machine-learning algorithms, i.e., Backpropagation Neural
Network (BNN), Random Forest (RF), Naive Bayes (NB)
and Support Vector Machine (SVM), were used to classify
plants under different phosphorus fertilizations at
Table 5 Chosen features of the classifiers used in the study
Name of WEKA
classifier’s library
Algorithm description Acronym Used parameters
Multilayer Perceptron Neural networks with backpropagation used for tuning the weights of a neural net
based on the error rate (i.e. loss).
BNN AutoBuild: true;
Learning rate: 0.3;
Momentum: 0.1;
Training time: 500
Hidden layers = 25
LibSVM This library enables users to deal with One-class SVM, Regressing SVM, and nu-SVM.
Many useful statistics are allowed including confusion matrix, precision estimation,
ROC score.
LIBSVM SVM Type: nu-SVC;
Kernel Type: radial basis
function;
Nu: 0.g;
gamma: 0.1;
degree: 3
Normalize: true;
Probability Estimates:
true
Logistic Used for building and using a multinomial logistic regression model with a ridge
estimator.
LOG Debug: false;
MaxIts: −1;
Ridge: 1.0E-6
Random Forests This classifier enables to create forest of random trees. It induces each constituent
decision tree from a bootstrap sample of the training data
RF Debug: false;
MaxDepth: 0;
Num of Features: 0;
Num of Trees: 10;
Seed: 1
Siedliska et al. BMC Plant Biology           (2021) 21:28 Page 14 of 17

different developmental stages. Extensive work has been
performed to optimize the parameters of individual
models using trial and error. The parameters of the elabo-
rated models are described in Table 5. For the classifica-
tion experiment, samples were randomly selected for the
test set and the validation set at the ratio 75:25. The train-
ing data set was used to build the classification model,
while the test data set was used to check the model ’ sc a p -
ability to properly classify new samples. The experiment
of learning and testing was repeated 10 times with the
random data selection (cross-validation method). All clas-
sification algorithms were implemented from a compre-
hensive software called the Waikato Environment for
Knowledge Analysis, or WEKA [ 68]. Initially, the majority
of available classifiers in these categories were tested on
representative groups of training and test data. The four
with the best prediction accuracies were chosen for
comparison.
Reference analysis
At the end of the experiment, fresh leaves from each plant
were clipped from the canopy with a pair of scissors, put
in plastic bags, frozen in a cooler and brought to the la-
boratory for measurements of leaf pigments and nutri-
tional element content. To determine the chlorophyll
content, fresh leaves (approximately 0.6 g) were ground in
80% acetone solution. Then, the leaf chlorophyll concen-
tration was measured using a UV-VIS spectrophotometer
(UV-5600, Metash, China) according to the method de-
scribed by Lichtenthaler [ 69]. The rest of the plant sam-
ples were oven-dried (105 °C for 0.5 h followed by 80 °C
until the constant weight was attained) and then ground
into fine powder for mineral content analysis. The total P
content was quantified spectrophotometrically using the
vanado-molybdate phosphoric acid yellow colour method
[70]. Total N content was determined by the micro Kjel-
dahls’ method. Total K concentration in the leaf was ana-
lysed using the flame-photometric method. The calcium
content (Ca) and magnesium (Mg) content were deter-
mined using an atomic absorption spectrometer (Spektr
AA 800, Varian, CA, USA).
Statistical analyses
To test the effects of P fertilizer treatments on leaf
photosynthetic pigments and nutritional elements, one-
way analysis of variance (ANOVA) was followed by
Tukey’ s honest significant difference (HSD). P< 0.05 was
considered statistically significant. Pearson ’ s correlation
coefficient (R) was also used to test the relationship be-
tween leaf biochemical constituents, P fertilization and
parts of the plants. All these statistical analyses were
conducted using STATISTICA v13.4 (TIBCO Software
Inc., Palo Alto, California, United States).
Supplementary Information
The online version contains supplementary material available at https://doi.
org/10.1186/s12870-020-02807-4.
Additional file 1: Table S1. Confusion matrices created for random
forest (RF) models of phosphorous content in the treatments for three
studied species (sugar beet – in blue, celery – in green and strawberry –
in red) at five stages of plant growth.
Abbreviations
VNIR: Visible and near infrared; PCC: Pearson correlation coefficients;
ROI: Regions of interest; SWIR: Short-wave infrared; CFS: Correlation-based
feature selection; NIR: Near infrared; DAT: Days after transplanting;
SG: Savitzky-Golay; GS: Greedy-stepwise; UV-VIS: Ultraviolet-visible;
BNN: Backpropagation neural network; RF: Random forest; NB: Naive Bayes;
SVM: Support vector machine; WEKA: Waikato environment for knowledge
analysis; ANOVA: Analysis of variance; HSD: Honest significant difference
Acknowledgements
Not applicable.
Authors’ contributions
AS, JPW, MZ, and JK performed the experiments. AS and PB designed the
experiments and wrote the paper. JK and PB discussed the results and
contributed to the final manuscript. All authors in the “Contributions” section
have read and approved the manuscript.
Funding
This paper was partly financed from funds of the Polish National Centre for
Research and Development in frame of the project: “MSINiN”, contract
number: BIOSTRATEG3/343547/8/NCBR/2017. The funding source had no
role in the design of this study, nor in data collection analyses or
interpretation, decision to publish results or in preparation of the manuscript.
Availability of data and materials
The datasets generated during the current study are available from the
corresponding author on reasonable request after consulting the project
funder.
Ethics approval and consent to participate
Not applicable.
Consent for publication
Not applicable.
Competing interests
The authors declare that they have no competing interests.
Author details
1Institute of Agrophysics, Polish Academy of Sciences, ul. Do świadczalna 4,
20-290 Lublin, Poland. 2Department of Biophysics, Institute of Physics, Maria
Curie-Skłodowska University, 20-031 Lublin, Poland.
Received: 24 July 2020 Accepted: 20 December 2020
References
1. Shen J, Yuan L, Zhang J, Li H, Bai Z, Chen X, et al. Phosphorus dynamics:
from soil to plant. Plant Physiol. 2011;156:997 –1005.
2. Vance CP, Uhde-Stone C, Allan DL. Phosphorus acquisition and use: critical
adaptations by plants for securing a nonrenewable resource. New Phytol.
2003;157:423–47.
3. Li Y, Wang T, Li J, Ao Y. Effect of phosphorus on celery growth and nutrient
uptake under different calcium and magnesium levels in substrate culture.
Hortic Sci. 2010;37:99 –108.
4. Bar łóg P, Grzebisz W, Fe ć M, Łukowiak R, Szczepaniak W. Row method of
sugar beet ( Beta vulgaris L.) fertilization with multicomponent fertilizer
based on urea-ammonium nitrate solution as a way to increase nitrogen
efficiency. J Cent Eur Agric. 2010;11:225 –34.
Siedliska et al. BMC Plant Biology           (2021) 21:28 Page 15 of 17

5. Salimpour S, Khavazi K, Nadian H, Besharati H, Miransari M. Enhancing
phosphorous availability to canola (Brassica napus L.) using P solubilizing
and sulfur oxidizing bacteria. Aust J Crop Sci. 2010;4:330 –4.
6. Zhang X, Liu F, He Y, Gong X. Detecting macronutrients content and
distribution in oilseed rape leaves based on hyperspectral imaging. Biosyst
Eng. 2013;115:56–65.
7. Choi JM, Lee CW. Influence of elevated phosphorus levels in nutrient
solution on micronutrient uptake and deficiency symptom development in
strawberry cultured with fertigation system. J Plant Nutr. 2012;35:1349 –58.
8. Viégas I de JM, Cordeiro RAM, Almeida GM de, Silva DAS, Silva BC da,
Okumura RS, et al. Growth and visual symptoms of nutrients deficiency in
Mangosteens (Garcinia mangostana L.) Am J Plant Sci 2018;9:1014 –1028.
9. Osborne SL, Schepers JS, Francis DD, Schlemmer MR. Detection of
phosphorus and nitrogen deficiencies in corn using spectral radiance
measurements. Agron J. 2002;94:1215.
10. Ticconi CA, Abel S. Short on phosphate: plant surveillance and
countermeasures. Trends Plant Sci. 2004;9:548 –55.
11. Dunn BL, Singh H, Payton M, Kincheloe S. Effects of nitrogen, phosphorus,
and potassium on SPAD-502 and atLEAF sensor readings of salvia. J Plant
Nutr. 2018;41:1674 –83.
12. Yaryura P, Cordon G, Leon M, Kerber N, Pucheu N, Rubio G, et al. Effect of
phosphorus deficiency on reflectance and chlorophyll fluorescence of cotyledons of
oilseed rape (Brassica napusL.). J Agron Crop Sci. 2009;195:186–96.
13. Li G, Wang C, Feng M, Yang W, Li F, Feng R. Hyperspectral prediction of leaf
area index of winter wheat in irrigated and rainfed fields. Plos One. 2017;12:
e0183338.
14. Wu W, Li J, Zhang Z, Ling C, Lin X, Chang X. Estimation model of LAI and
nitrogen content in tea tree based on hyperspectral image. Trans Chin Soc
Agric Eng. 2018;34:195 –201.
15. Guo T, Tan C, Li Q, Cui G, Li H. Estimating leaf chlorophyll content in
tobacco based on various canopy hyperspectral parameters. J Ambient
Intell Humaniz Comput. 2019;10:3239 –47.
16. Ling B, Goodin DG, Raynor EJ, Joern A. Hyperspectral analysis of leaf
pigments and nutritional elements in tallgrass prairie vegetation. Front Plant
Sci. 2019;10:142.
17. Szuvandzsiev P, Helyes L, Lugasi A, Szántó C, Baranowski P, Pék Z.
Estimation of antioxidant components of tomato using VIS-NIR reflectance
data by handheld portable spectrometer. Int Agrophysics. 2014;28:521 –7.
18. Wang Y, Hu X, Jin G, Hou Z, Ning J, Zhang Z. Rapid prediction of
chlorophylls and carotenoids content in tea leaves under different levels of
nitrogen application based on hyperspectral imaging. J Sci Food Agric.
2019;99:1997–2004.
19. Sytar O, Zivcak M, Neugart S, Brestic M. Assessment of hyperspectral
indicators related to the content of phenolic compounds and multispectral
fluorescence records in chicory leaves exposed to various light
environments. Plant Physiol Biochem. 2020;154:429 –38.
20. Zhao YR, Li X, Yu KQ, Cheng F, He Y. Hyperspectral imaging for determining
pigment contents in cucumber leaves in response to angular leaf spot
disease. Sci Rep. 2016;6:27790.
21. Sytar O, Br ϋckovά K, Kovar M, Ž ivčák M, Hemmerich I, Bresti č M.
Nondestructive detection and biochemical quantification of buckwheat
leaves using visible (VIS) and near-infrared (NIR) hyperspectral reflectance
imaging. J Cent Eur Agric. 2017;18:864 –78.
22. Wang C, Nie S, Xi X, Luo S, Sun X. Estimating the biomass of maize with
hyperspectral and LiDAR data. Remote Sens. 2017;9:11.
23. Adam E, Deng H, Odindi J, Abdel-Rahman EM, Mutanga O. Detecting the
early stage of Phaeosphaeria leaf spot infestations in maize crop using in
situ hyperspectral data and guided regularized random Forest algorithm. J
Spectrosc. 2017;6961387:1–8.
24. Baranowski P, Jedryczka M, Mazurek W, Babula-Skowronska D, Siedliska A,
Kaczmarek J. Hyperspectral and thermal imaging of oilseed rape (Brassica
napus) response to fungal species of the genus Alternaria. Plos One. 2015;
10:e0122913.
25. Navrozidis I, Alexandridis TK, Dimitrakos A, Lagopodi AL, Moshou D, Zalidis
G. Identification of purple spot disease on asparagus crops across spatial
and spectral scales. Comput Electron Agric. 2018;148:322 –9.
26. Siedliska A, Baranowski P, Zubik M, Mazurek W, Sosnowska B. Detection of
fungal infections in strawberry fruit by VNIR/SWIR hyperspectral imaging.
Postharvest Biol Technol. 2018;139:115 –26.
27. Kovar M, Brestic M, Sytar O, Barek V, Hauptvogel P, Zivcak M. Evaluation of
hyperspectral reflectance parameters to assess the leaf water content in
soybean. Water. 2019;11:443.
28. Surase RR, Kale KV, Varpe AB, Vibhute AD, Gite HR, Solankar MM, et al.
Estimation of water contents from vegetation using hyperspectral indices.
In: Panda G, Satapathy SC, Biswal B, Bansal R, editors. Microelectronics,
Electromagnetics and Telecommunications. Singapore: Springer; 2019. p.
247–55.
29. Liang L, Qin Z, Zhao S, Di L, Zhang C, Deng M, et al. Estimating crop
chlorophyll content with hyperspectral vegetation indices and the hybrid
inversion method. Int J Remote Sens. 2016;37:2923 –49.
30. Feng H, Chen G, Xiong L, Liu Q, Yang W. Accurate digitization of the
chlorophyll distribution of individual rice leaves using hyperspectral imaging
and an integrated image analysis pipeline. Front Plant Sci. 2017;8:1238.
31. Corti M, Marino Gallina P, Cavalli D, Cabassi G. Hyperspectral imaging of
spinach canopy under combined water and nitrogen stress to estimate
biomass, water, and nitrogen content. Biosyst Eng. 2017;158:38 –50.
32. Wang Y, Hu X, Hou Z, Ning J, Zhang Z. Discrimination of nitrogen fertilizer
levels of tea plant (Camellia sinensis) based on hyperspectral imaging. J Sci
Food Agric. 2018;98:4659 –64.
33. Lu J, Yang T, Su X, Qi H, Yao X, Cheng T, et al. Monitoring leaf potassium
content using hyperspectral vegetation indices in rice leaves. Precis Agric.
2020;21:324–48.
34. Li D, Wang C, Jiang H, Peng Z, Yang J, Su Y, et al. Monitoring litchi canopy
foliar phosphorus content using hyperspectral data. Comput Electron Agric.
2018;154:176–86.
35. Liu Y, Lyu Q, He S, Yi S, Liu X, Xie R, et al. Prediction of nitrogen and
phosphorus contents in citrus leaves based on hyperspectral imaging. Int J
Agric Biol Eng. 2015;8:80 –8.
36. Mahajan GR, Pandey RN, Sahoo RN, Gupta VK, Datta SC, Kumar D.
Monitoring nitrogen, phosphorus and Sulphur in hybrid rice (Oryza sativa L.)
using hyperspectral remote sensing. Precis Agric. 2017;18:736 –61.
37. Ansari MS, Young KR, Nicolas ME. Determining wavelength for nitrogen and
phosphorus nutrients through hyperspectral remote sensing in wheat
(Triticum aestivum L.) plant. Int J Bio-Resour Stress Manag. 2016;7:653 –62.
38. Li L, Wang S, Ren T, Wei Q, Ming J, Li J, et al. Ability of models with
effective wavelengths to monitor nitrogen and phosphorus status of winter
oilseed rape leaves using in situ canopy spectroscopy. Field Crops Res.
2018;215:173–86.
39. Christensen LK, Bennedsen BS, Jørgensen RN, Nielsen H. Modelling nitrogen
and phosphorus content at early growth stages in spring barley using
hyperspectral line scanning. Biosyst Eng. 2004;88:19 –24.
40. Mahajan GR, Sahoo RN, Pandey RN, Gupta VK, Kumar D. Using hyperspectral
remote sensing techniques to monitor nitrogen, phosphorus, Sulphur and
potassium in wheat (Triticum aestivum L.). Precis Agric. 2014;15:499 –522.
41. Backhaus A, Bollenbeck F, Seiffert U. Robust classification of the nutrition
state in crop plants by hyperspectral imaging and artificial neural networks.
In: 2011 3rd Workshop on Hyperspectral Image and Signal Processing:
Evolution in Remote Sensing (WHISPERS); 2011. p. 1 –4.
42. Sun Y, Gao J, Wang K, Shen Z, Chen L. Utilization of machine vision to
monitor the dynamic responses of rice leaf morphology and colour to nitrogen,
phosphorus, and potassium deficiencies. J Spectrosc. 2018;1469314:1–13.
43. Trejo-Téllez LI, Gómez-Merino F. Nutrient management in strawberry. Effects
on yield, quality and plant health. In: Strawberries: Cultivation,
Antioxidant Properties and Health Benefits. Nova Science Publishers,
Nathan Malone (Ed.); 2014. p. 239 –67.
44. Estrada-Ortiz E, Trejo-Téllez LI, Gómez-Merino FC, Nuñez-Escobar R, Sandoval-
Villa M. Biochemical responses in strawberry plants supplying phosphorus in the
form of phosphite. Rev Chapingo Ser Hortic. 2011;17:129–38.
45. Costa R, Calvete E, Schons J, Reginatto F. Chlorophyll content in strawberry
leaves produced under shading screens in greenhouse. Acta Hortic. 2012;
926:321–4.
46. Ebrahimi R, Ebrahimi F, Ahmadizadeh M. Effect of different substrates on
herbaceous pigments and chlorophyll amount of strawberry in hydroponic
cultivation system. Am Eurasian J Agric Environ Sci. 2012;12:154 –8.
47. Choi HG, Moon BY, Kang NJ. Correlation between strawberry (Fragaria
ananassa Duch.) productivity and photosynthesis-related parameters under
various growth conditions. Front Plant Sci. 2016;7:1607.
48. Kaya C, Akram NA, Ashraf M. Influence of exogenously applied nitric oxide
on strawberry (Fragaria × ananassa) plants grown under iron deficiency
and/or saline stress. Physiol Plant. 2019;165:247 –63.
Siedliska et al. BMC Plant Biology           (2021) 21:28 Page 16 of 17

49. Porcar-Castell A, Tyystjärvi E, Atherton J, Tol C, Flexas J, Pfündel E, et al.
Linking chlorophyll a fluorescence to photosynthesis for remote sensing
applications: mechanisms and challenges. J Exp Bot. 2014;65:4065 –95.
50. Streit N, Canterle L, Canto M, Hecktheuer L. The chlorophylls. Cienc Rural.
2015;35:748–55.
51. Pacumbaba RO, Beyl CA. Changes in hyperspectral reflectance signatures of
lettuce leaves in response to macronutrient deficiencies. Adv Space Res.
2011;48:32–42.
52. Spiers JM, Braswell JH. Influence of N, P, K, Ca, and Mg rates on leaf
macronutrient concentration of “Navaho” blackberry. Acta Hortic. 2002;585:
659–63.
53. Chang SX. Seedling sweetgum (Liquidambar styraciflua L.) half-sib family
response to N and P fertilization: growth, leaf area, net photosynthesis and
nutrient uptake. For Ecol Manag. 2003;173:281 –91.
54. Dordas C. Dry matter, nitrogen and phosphorus accumulation, partitioning
and remobilization as affected by N and P fertilization and source –sink
relations. Eur J Agron. 2009;30:129 –39.
55. Finkner RE, Grimes DW, Herron GM. Effect of plant spacing and fertilizer on
yield, purity, chemical constituents and evapotranspiration of sugar beets in
Kansas. II Chemical constituents. J Sugarbeet Res. 1964;12:699 –714.
56. Feret J-B, François C, Asner GP, Gitelson AA, Martin RE, Bidel LPR, et al.
PROSPECT-4 and 5: advances in the leaf optical properties model separating
photosynthetic pigments. Remote Sens Environ. 2008;112:3030 –43.
57. Zhai Y, Cui L, Zhou X, Gao Y, Fei T, Gao W. Estimation of nitrogen,
phosphorus, and potassium contents in the leaves of different plants using
laboratory-based visible and near-infrared reflectance spectroscopy:
comparison of partial least-square regression and support vector machine
regression methods. Int J Remote Sens. 2013;34:2502 –18.
58. Knox NM, Skidmore AK, Prins HHT, Heitkönig IMA, Slotow R, van der Waal C,
et al. Remote sensing of forage nutrients: combining ecological and spectral
absorption feature data. ISPRS J Photogramm Remote Sens. 2012;72:27–35.
59. Baranowski P, Mazurek W, Pastuszka-Wo źniak J. Supervised classification of
bruised apples with respect to the time after bruising on the basis of
hyperspectral imaging data. Postharvest Biol Technol. 2013;86:249 –58.
60. Vos J. Input and offtake of nitrogen, phosphorus and potassium in cropping
systems with potato as a main crop and sugar beet and spring wheat as
subsidiary crops. Eur J Agron. 1996;5:105 –14.
61. Biczak R, Herman B, Rychter P. Effects of nitrogen, phosphorus and
potassium fertilization on yield and biological value of leaf celery. Part I:
vegetables yield and mineral composition. Proc ECOpole. 2011;5:161 –71.
62. Das AK, Singh B, Sahoo RK. Correlation and path analysis in strawberry
(Fragaria ananassa Duch). Indian J Hortic. 2006;63:83 –5.
63. Ghaly F, Abd-Hady M, Abd-Elhamied A. Effect of varieties, phosphorus and
boron fertilization on sugar beet yield and its quality. J Soil Sci Agric Eng.
2019;10:115–22.
64. Feller C, Bleiholder H, Buhr L, Hack H, Hess M, Klose R, et al. Phanologische
Entwicklungsstadien von Gemusepflanzen II. Fruchtgemuse und
Hulsenfruchte. Nachr Dtsch Pflanzenschutzd. 1995;47:217 –32.
65. Meier U, Graf H, Hack H, Hess M, Kennel W, Klose R, et al. Phanologische
Entwicklungsstadien des Kernobstes (Malus domestica Borkh. und Pyrus
communis L.), des Steinobstes (Prunus-Arten), der Johannisbeere (Ribes-
Arten) und der Erdbeere (Fragaria x ananassa Duch.). Nachr Dtsch
Pflanzenschutzd. 1994;46:141 –53.
66. Ravikanth L, Jayas DS, White NDG, Fields PG, Sun D-W. Extraction of spectral
information from hyperspectral data and application of hyperspectral
imaging for food and agricultural products. Food Bioprocess Technol. 2017;
10:1–33.
67. Ozcift A, Gulten A. Classifier ensemble construction with rotation forest to
improve medical diagnosis performance of machine learning algorithms.
Comput Methods Prog Biomed. 2011;104:443 –51.
68. Witten IH, Frank E. Data mining: practical machine learning tools and
techniques, second edition. Amsterdam. Boston: Morgan Kaufmann; 2005.
69. Lichtenthaler HK. Chlorophylls and carotenoids: pigments of photosynthetic
biomembranes. Meth Enzymol. 1987;148:350 –82.
70. Jackson ML. Soil chemical analysis: advanced course. 2nd ed. Madison:
Parallel Press, University of Wisconsin-Madison Libraries; 2005.
Publisher’sN o t e
Springer Nature remains neutral with regard to jurisdictional claims in
published maps and institutional affiliations.
Siedliska et al. BMC Plant Biology           (2021) 21:28 Page 17 of 17
