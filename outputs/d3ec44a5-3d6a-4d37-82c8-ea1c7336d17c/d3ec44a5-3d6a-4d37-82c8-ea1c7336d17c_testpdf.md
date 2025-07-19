This article was downloaded by: [45.250.34.100] On: 02 January 2025, At: 19:02 Publisher: Institute for Operations Research and the Management Sciences (INFORMS) INFORMS is located in Maryland, USA

![](_page_0_Picture_1.jpeg)

### Marketing Science

Publication details, including instructions for authors and subscription information: <http://pubsonline.informs.org>

# Regional Poverty Alleviation Partnership and E-Commerce Trade

Zemin (Zachary) Zhong, Wenyu Zhou, Jiewei Li, Peng Li

To cite this article:

Zemin (Zachary) Zhong, Wenyu Zhou, Jiewei Li, Peng Li (2024) Regional Poverty Alleviation Partnership and E-Commerce Trade. Marketing Science

Published online in Articles in Advance 23 May 2024

.<https://doi.org/10.1287/mksc.2023.0214>

Full terms and conditions of use: [https://pubsonline.informs.org/Publications/Librarians-Portal/PubsOnLine-](https://pubsonline.informs.org/Publications/Librarians-Portal/PubsOnLine-Terms-and-Conditions)[Terms-and-Conditions](https://pubsonline.informs.org/Publications/Librarians-Portal/PubsOnLine-Terms-and-Conditions)

This article may be used only for the purposes of research, teaching, and/or private study. Commercial use or systematic downloading (by robots or other automatic processes) is prohibited without explicit Publisher approval, unless otherwise noted. For more information, contact permissions@informs.org.

The Publisher does not warrant or guarantee the article's accuracy, completeness, merchantability, fitness for a particular purpose, or non-infringement. Descriptions of, or references to, products or publications, or inclusion of an advertisement in this article, neither constitutes nor implies a guarantee, endorsement, or support of claims made of that product, publication, or service.

Copyright © 2024 The Author(s)

Please scroll down for article—it is on subsequent pages

![](_page_0_Picture_15.jpeg)

With 12,500 members from nearly 90 countries, INFORMS is the largest international association of operations research (O.R.) and analytics professionals and students. INFORMS provides unique networking and learning opportunities for individual professionals, and organizations of all types and sizes, to better understand and use O.R. and analytics tools and methods to transform strategic visions and achieve better outcomes. For more information on INFORMS, its publications, membership, or meetings visit <http://www.informs.org>

![](_page_1_Picture_1.jpeg)

# **Regional Poverty Alleviation Partnership and E-Commerce Trade**

Zemin (Zachary) Zhong,<sup>a</sup> Wenyu Zhou,<sup>b,c,\*</sup> Jiewei Li,<sup>d</sup> Peng Li<sup>e</sup>

**<sup>a</sup>**Rotman School of Management, University of Toronto, Toronto, Ontario M5S 3E6, Canada; **<sup>b</sup>** International Business School, Zhejiang University, Haining, Zhejiang 314400, China; **<sup>c</sup>** School of Economics, Zhejiang University, Hangzhou, Zhejiang 310058, China; **<sup>d</sup>** Faculty of Business and Economics, University of Lausanne, 1015 Lausanne, Switzerland; **e**AliResearch, Alibaba Group, Hangzhou 310023, China

\*Corresponding author

Contact: [zachary.zhong@rotman.utoronto.ca](mailto:zachary.zhong@rotman.utoronto.ca), D<https://orcid.org/0000-0003-4374-6964> (Z(Z)Z); [wenyuzhou@intl.zju.edu.cn,](mailto:wenyuzhou@intl.zju.edu.cn)  $\bigcirc$ <https://orcid.org/0000-0002-9176-5433> (WZ); [jiewei.li.24@ucl.ac.uk,](mailto:jiewei.li.24@ucl.ac.uk)  $\bigcirc$ <https://orcid.org/0000-0003-3243-4009> (JL); [marx.lp@taobao.com](mailto:marx.lp@taobao.com) (PL)

**Received:** May 26, 2023 **Revised:** December 6, 2023; February 13, 2024 **Accepted:** April 2, 2024 **Published Online in Articles in Advance:**  May 23, 2024, and updated October 29, 2024

**<https://doi.org/10.1287/mksc.2023.0214>** 

**Copyright:** © 2024 The Author(s)

**Abstract.** Regional inequalities are prevalent in all major economies. What are the effects of inclusive growth policies targeting economically disadvantaged regions? In this study, we examine how the East-West Poverty Alleviation Partnership, which pairs rich cities in East China with economically disadvantaged cities in West China, affects e-commerce trade. Using proprietary trade-flow data from Alibaba, we find that the partnership boosts e-commerce trade between partnered cities. This effect is asymmetric as it increases exports from West China to East China but not the other way around. The effect is also particularly strong for product categories in which West China has a comparative advantage and for the western regions with the largest economic and development disparities. Additionally, the results indicate that the partnership benefits both big and small sellers equally. In exploring the underlying mechanisms, we find that partnership-driven migration as well as consumer awareness can partially explain the effect.

**History:** Olivier Toubia served as the senior editor. This paper has been accepted for the *Marketing Science* Special Section on DEI.

**Open Access Statement:** This work is licensed under a Creative Commons Attribution 4.0 International License. You are free to copy, distribute, transmit and adapt this work, but you must attribute this work as "*Marketing Science*. Copyright © 2024 The Author(s). [https://doi.org/10.1287/mksc.2023.](https://doi.org/10.1287/mksc.2023.0214) [0214](https://doi.org/10.1287/mksc.2023.0214), used under a Creative Commons Attribution License: [https://creativecommons.org/licenses/](https://creativecommons.org/licenses/by/4.0/)  $by/4.0/$ ."

**Funding:** The research of W. Zhou is funded by the Zhejiang Provincial Philosophy and Social Sciences Planning Project [Grant 24NDJC125YB], the National Natural Science Foundation of China [Grants 72203200 and 72141305], the National Key Research and Development Program of China [Grant 2022YFF0902000], the Soft Science Research Program of Zhejiang Province [Grant 2023C35101], the National Statistical Science Research Project of China [Grant 2023LZ040], and the Fundamental Research Funds for General Universities [Grant S20240048].

**Supplemental Material:** The online appendix and data files are available at [https://doi.org/10.1287/mksc.](https://doi.org/10.1287/mksc.2023.0214) [2023.0214.](https://doi.org/10.1287/mksc.2023.0214)

**Keywords: inequality** • **inclusive growth** • **e-commerce** • **China**

#### **1. Introduction**

Regional inequalities are prevalent in all major economies, including the economic gap between the heartland and coast regions in the United States, East Europe, and West Europe as well as East and West China. In response, governments have introduced various place-based policies aimed at promoting inclusive growth, reducing inequalities, and alleviating poverty. E-Commerce platforms, by offering businesses access to markets and reducing barriers to entrepreneurship, have the potential to contribute to these inclusive growth policies. This is particularly relevant in remote areas and among ethnic minorities, where physical and

cultural distances can pose substantial hurdles. In this paper, we empirically examine the impact of one of China's most extensive poverty-alleviation policies on e-commerce.

Despite China's miraculous economic growth, poverty remains a prevalent issue in West China, home to most of the country's ethnic minorities. As of 2012, over 50 million people, representing 17.6% of the local population in this region, lived in poverty. In stark contrast, poverty was virtually eliminated in the eastern provinces, where Gross Domestic Product (GDP) per capita was 87% higher than in West China in 2012. Even in 2021, this gap remained significant at 68%. To address regional inequality and poverty, the Chinese Central Government established the East-West Poverty Alleviation Partnership, which pairs western regions with their eastern counterparts. Eastern local governments are charged with providing financial aid and other forms of support, such as governance expertise, technology, market access, and labor exports, to their partnered cities in West China. Over the past few years, this partnership has facilitated the migration of millions of people from west to east and prompted billions of investments that created hundreds of thousands of local jobs in West China. These initiatives have played a significant role in lifting tens of millions of West China residents out of poverty. Yet, despite the importance and scale of this partnership, to the best of our knowledge, there has been no study on its economic effects.

We evaluate the economic impact of the regional partnership plan through e-commerce trade. Unlike financial aid, which typically involves zero-sum transfers between regions, trade often generates surpluses. E-Commerce, constituting about one fourth of all consumption in China, is particularly relevant in this context as e-commerce can potentially reduce transportation costs and trade barriers for cities between East and West China, which are often more than a thousand miles apart (Goldfarb and Tucker 2019). Consequently, this has the potential to help businesses in economically disadvantaged West China access the vast East China market. Our analysis is based on trade flow data derived from all transactions on Alibaba, the leading e-commerce platform in China. The data, aggregated on a monthly basis at the prefecture-city pair level from 2017 to 2021, total 1.15 million observations.

We first present empirical patterns using the classic gravity model. We document that being city partners is associated with a 5.6% increase in e-commerce trade. Notably, this association is only significant for west to east trade (11.9%). However, this pattern should not be interpreted as causal because of potential systematic differences between partnered city pairs and nonpartnered ones. We thus further use a spatial regression discontinuity (RD) design for causal identification. This design is implemented by comparing partnership pairs with control pairs in close proximity, which should share similar unobserved demand for goods produced in the other cities, as well as similar unobserved trade barriers. We verify that within close proximity, partnership and control pairs are balanced in terms of observables.

We find that the partnership caused a 4.8% increase in e-commerce trade flow, which translates to an increase of 2–3 billion Chinese yuan in trade. The effect is asymmetric; from east to west, the impact is minimal and statistically insignificant, whereas from west to east, it is substantial (10.0%) and statistically significant. The effects on the number of transactions are qualitatively similar. The results are robust across various specifications and bandwidth choices and with different types of control city pairs as well as under alternative implementations of spatial RD.

We also investigate the heterogeneous effects on different sellers by examining the impact on the sellers' concentration ratio for each city pair-month cell. Our findings indicate that the partnership does not influence the sellers' concentration ratio, suggesting that the policy equally benefits large and small sellers in West China. Among different product categories, the effect is notably strong for food and beverage, clothing, and household goods, with exports from west to east increasing by 12%–9.6% because of the partnership. These sectors are comparative advantages of West China and priority investments by the policy to create local jobs.

We further examine how the effects vary across cities with different characteristics. Our findings reveal that pairs with larger GDP gaps or western cities with worse physical and digital infrastructure exhibit stronger effects. Western cities with higher proportions of ethnic minorities, more geographical indication (GI) products, and more e-commerce firms benefit more from the partnership, suggesting that the policy can help overcome cultural barriers as well as unlock the supply-side potential in e-commerce. Dynamically, whereas the overall effects decreased following the coronavirus disease 2019 (COVID-19) pandemic, the effect from west to east remained consistent as before.

In testing the mechanism, we find that migration between partnered cities partially explains the effect. Thus, the partnership addresses inequality in two ways; it assists migrant workers from West China in securing jobs in eastern cities who in turn, support sellers in their hometowns through e-commerce. Consumer awareness, as measured by online search, also partially mediates the effect. We find no evidence supporting the effect being driven by targeted public-sector spending, typically observed at the end of the year or during the Chinese New Year (CNY), nor by reduced transportation costs between partnered cities as measured by direct flight routes.

This study carries broad and significant implications for both policymakers and platforms. Our results suggest that the partnership plan boosts e-commerce trade between regional pairs, particularly from economically disadvantaged regions to more developed ones. The benefits are equitably distributed among both large and small sellers. This experience from the world's largest e-commerce platform also holds implications for other economies, where the debate on whether digitization exacerbates or alleviates inequality remains active and ongoing.

We are the first to examine the economic effects of the regional cooperation plan, thereby contributing to the literature on inequality, local economic development, and e-commerce trade. The primary policy we <span id="page-3-0"></span>infrastructure, shipping services, and training for sellers to host online storefronts or live stream e-commerce sessions. Whereas many of these investments may increase the aided regions' overall exports, some may specifically increase exports to the paired eastern regions. For example, the product categories that eastern firms invest in may correlate with their local preferences. Shipping routes, such as new airline networks, may reduce the specific transportation costs between partnership pairs. On the demand side, local governments in East China can promote products from their paired regions through advertising, channel support, coupons, and consumer subsidies. Other policy initiatives, such as labor exports, may also indirectly increase trade flow.

### **3. Data**

Our study utilizes data from several sources. The key variation is the East-West Poverty Alleviation

**Table 1.** Summary Statistics

Partnership from the Yearbook of China's Poverty Alleviation and Development. The outcome variable is the trade flow data from Alibaba Group, the largest e-commerce company in China. We supplement these two data sets with city pair characteristics, migration, and Baidu search index data.

#### **3.1. City Partnerships**

We collect the list of city partnerships (Online Appendix Table A.1) reported in the 2018 Yearbook of China's Poverty Alleviation and Development, published by the State Council Leading Group of Poverty Alleviation and Development.<sup>2</sup> Within all 87 eastern cities and 110 western cities, there are  $19,140$   $(2 \times 87 \times 110)$  directed city pairs.<sup>3</sup> There are 56 eastern cities and 81 western cities in the program, forming 256 directed partnership pairs, based on which we define the treatment indicator *Partnership\_pair<sub>ij</sub>* that equals one if city *i* and city *j* are "partner cities" under the framework of the East-West

Variable Observations Mean SD Min P25 P50 P75 Max Panel A: City partnerships *Partnership pair* 19,140 0.013 0.115 0.00 0.00 0.00 0.00 1.00 Panel B: E-Commerce trade flows (full sample) *Trade amount* 1,148,400 6,710,610.75 35,489,376.75 0.00 81,174.18 455,479.42 1,298,604.85 3,330,035,240.52 *Deal volume* 1,148,400 37,620.12 246,761.85 0.00 767.21 3,622.76 19,610.40 19,812,880.78 *Seller concentration ratio* 1,136,426 88.56 13.77 18.51 80.74 89.22 97.47 99.99

Panel C: E-Commerce trade flows (east to west sample) *Trade amount* 574,200 9,062,917.15 57,932,763.85 0.00 300,124.01 892,274.52 5,339,022.40 2,920,621,699.07 *Deal volume* 574,200 115,145.46 589,621.79 0.00 2,975.83 12,983.27 34,234.36 25,296,946.13 *Seller concentration ratio* 574,134 88.08 11.87 20.65 81.21 88.27 95.55 99.98

*Buyer concentration ratio* 1,137,650 82.32 14.64 14.69 72.88 82.55

<span id="page-4-0"></span>![](_page_4_Figure_1.jpeg)

![](_page_4_Figure_2.jpeg)

*Note*. This figure displays the city partnerships, represented by red dashed lines, between the targeted western cities (green circles) and their corresponding eastern partner cities (blue squares).

Poverty Alleviation Partnership. Panel A of Table [1](#page-3-0) reports the summary statistics of this variable for the full sample. These city partnerships were first announced at the beginning of 2017 by the central government, and they remained the same throughout our sample period.<sup>4</sup> Figure 1 illustrates the pairs on a map. The rest are potential control pairs, of which we can further classify them into four types. (1) Neither eastern city *i* nor western city *j*  are in the program (1,798 pairs). (2) Only eastern city *i* is in the program (3,248 pairs). (3) Only western city *j* is in the program (5,022 pairs). (4) Both eastern city *i* and western city *j* are in the program, but they are not in a partnership pair with each other (8,816 pairs). We will show that our results are robust to various combinations of control pairs.

#### **3.2. E-Commerce Trade Flows**

The e-commerce trade flow data used in our study consist of four key outcome variables, including trade amount in Chinese yuan (*trade*), the number of deals or transactions (*deal*), seller concentration ratio, and buyer concentration ratio, for each directed city pair on a monthly basis. These variables are constructed using transaction-level data from Taobao and Tmall, the most popular online retail platforms in China, which are both owned by the Alibaba Group. Specifically, for the trade flow from city *i* to city *j*, the seller (respectively, buyer) concentration ratio is defined as the share of the trade amount of the top 10% largest sellers (respectively, buyers) measured by the transaction amount in city *i* (respectively, city *j*) relative to the total monthly trade flow between these two cities.

Panels B, C, and D of Table [1](#page-3-0) report the summary statistics of the outcome variables for the full, east to west, and west to east samples, respectively. The final data set consists of the e-commerce trade flows of 19,140 directed city pairs from January 2017 to December 2021, resulting in a sample size of  $1,148,400$  (19, 140  $\times$  60 months). The east to west e-commerce trade flows are an order of magnitude larger than those in the other direction as the e-commerce industry is much more developed in the eastern region of China. There are a few missing data points in the two concentration ratios because of zero trade in these city pair-month cells. In Online Appendix Table A.2, we further show the summary statistics of the share of partnered cities relative to the overall east-west trade. On average, the trade between partnered cities is about 4.78% of the overall east-west trade, whereas western cities' exports to partnered cities constitute 5% of their overall export to all eastern cities.