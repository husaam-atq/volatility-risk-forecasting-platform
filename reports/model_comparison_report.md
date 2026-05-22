# Model Comparison Report

## Executive Summary

The modelling layer compares rolling realised-volatility baselines, EWMA, GARCH-family models, tree-based regressors and ensemble forecasts on identical out-of-sample dates.
QLIKE is treated as the primary metric because it is robust for volatility forecast comparison and penalises variance underestimation.

## Aggregate Test-Period Ranking

| model | asset_count | avg_qlike | avg_mae | avg_rmse | avg_rank | top_two_share | improvement_vs_rolling_21 | improvement_vs_ewma | improvement_vs_garch |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| har_rolling_update | 10 | 0.1813 | 0.0196 | 0.0294 | 1.5000 | 0.8000 | 0.0063 | 0.0476 | 0.0831 |
| gjr_rolling_update | 10 | 0.1814 | 0.0189 | 0.0293 | 2.1000 | 0.7000 | 0.0062 | 0.0475 | 0.0830 |
| garch_rolling_update | 10 | 0.1814 | 0.0187 | 0.0293 | 2.6000 | 0.4000 | 0.0061 | 0.0474 | 0.0830 |
| ewma_rolling_update | 10 | 0.1814 | 0.0188 | 0.0293 | 3.8000 | 0.1000 | 0.0061 | 0.0474 | 0.0829 |
| rolling_21 | 10 | 0.1842 | 0.0245 | 0.0405 | 5.4000 | 0.0000 | 0.0000 | 0.0416 | 0.0774 |
| previous_day_rv | 10 | 0.1842 | 0.0245 | 0.0405 | 5.4000 | 0.0000 | 0.0000 | 0.0416 | 0.0774 |
| simple_average_ensemble | 10 | 0.1849 | 0.0315 | 0.0436 | 6.8000 | 0.0000 | -0.0017 | 0.0400 | 0.0759 |
| validation_weighted_ensemble | 10 | 0.1849 | 0.0315 | 0.0436 | 6.8000 | 0.0000 | -0.0017 | 0.0400 | 0.0759 |
| random_forest | 10 | 0.1907 | 0.0399 | 0.0660 | 9.2000 | 0.0000 | -0.0174 | 0.0251 | 0.0615 |
| hist_gradient_boosting | 10 | 0.1924 | 0.0441 | 0.0705 | 10.2000 | 0.0000 | -0.0215 | 0.0212 | 0.0578 |
| ewma_tuned | 10 | 0.1991 | 0.0566 | 0.0746 | 10.8000 | 0.0000 | -0.0326 | 0.0104 | 0.0476 |
| ewma_094 | 10 | 0.2047 | 0.0614 | 0.0796 | 11.8000 | 0.0000 | -0.0435 | 0.0000 | 0.0375 |
| gjr_garch | 10 | 0.2183 | 0.0789 | 0.1014 | 13.1000 | 0.0000 | -0.0732 | -0.0286 | 0.0106 |
| garch_11 | 10 | 0.2227 | 0.0834 | 0.1078 | 13.5000 | 0.0000 | -0.0853 | -0.0398 | 0.0000 |
| rolling_63 | 10 | 0.2760 | 0.1248 | 0.1595 | 15.0000 | 0.0000 | -0.1943 | -0.1443 | -0.1008 |

## Asset-Level Test-Period Ranking

| asset | model | qlike | mae | rmse | rank_qlike | improvement_vs_rolling_21 | improvement_vs_ewma | improvement_vs_garch |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AAPL | gjr_rolling_update | 0.6215 | 0.0230 | 0.0344 | 1 | 0.0050 | 0.0382 | 0.0632 |
| AAPL | har_rolling_update | 0.6215 | 0.0239 | 0.0345 | 2 | 0.0049 | 0.0382 | 0.0631 |
| AAPL | garch_rolling_update | 0.6215 | 0.0225 | 0.0345 | 3 | 0.0049 | 0.0382 | 0.0631 |
| AAPL | ewma_rolling_update | 0.6215 | 0.0233 | 0.0344 | 4 | 0.0049 | 0.0381 | 0.0631 |
| AAPL | simple_average_ensemble | 0.6244 | 0.0362 | 0.0490 | 5 | 0.0003 | 0.0336 | 0.0587 |
| AAPL | validation_weighted_ensemble | 0.6244 | 0.0362 | 0.0490 | 5 | 0.0003 | 0.0336 | 0.0587 |
| AAPL | previous_day_rv | 0.6246 | 0.0303 | 0.0482 | 7 | 0.0000 | 0.0334 | 0.0585 |
| AAPL | rolling_21 | 0.6246 | 0.0303 | 0.0482 | 7 | 0.0000 | 0.0334 | 0.0585 |
| AAPL | random_forest | 0.6266 | 0.0434 | 0.0652 | 9 | -0.0032 | 0.0303 | 0.0555 |
| AAPL | hist_gradient_boosting | 0.6292 | 0.0549 | 0.0780 | 10 | -0.0073 | 0.0263 | 0.0516 |
| AAPL | ewma_tuned | 0.6380 | 0.0655 | 0.0849 | 11 | -0.0215 | 0.0126 | 0.0382 |
| AAPL | ewma_094 | 0.6462 | 0.0733 | 0.0961 | 12 | -0.0346 | 0.0000 | 0.0260 |
| AAPL | gjr_garch | 0.6573 | 0.0940 | 0.1225 | 13 | -0.0523 | -0.0172 | 0.0092 |
| AAPL | garch_11 | 0.6634 | 0.1015 | 0.1315 | 14 | -0.0621 | -0.0266 | 0.0000 |
| AAPL | rolling_63 | 0.7258 | 0.1524 | 0.1962 | 15 | -0.1620 | -0.1232 | -0.0941 |
| GLD | har_rolling_update | -1.1049 | 0.0104 | 0.0190 | 1 | 0.0027 | 0.0291 | 0.0481 |
| GLD | garch_rolling_update | -1.1047 | 0.0105 | 0.0190 | 2 | 0.0026 | 0.0290 | 0.0480 |
| GLD | gjr_rolling_update | -1.1047 | 0.0105 | 0.0189 | 3 | 0.0026 | 0.0290 | 0.0480 |
| GLD | ewma_rolling_update | -1.1046 | 0.0101 | 0.0190 | 4 | 0.0025 | 0.0289 | 0.0479 |
| GLD | previous_day_rv | -1.1019 | 0.0132 | 0.0251 | 5 | 0.0000 | 0.0263 | 0.0452 |
| GLD | rolling_21 | -1.1019 | 0.0132 | 0.0251 | 5 | 0.0000 | 0.0263 | 0.0452 |
| GLD | random_forest | -1.1016 | 0.0150 | 0.0256 | 7 | -0.0002 | 0.0261 | 0.0450 |
| GLD | hist_gradient_boosting | -1.1010 | 0.0165 | 0.0262 | 8 | -0.0008 | 0.0255 | 0.0444 |
| GLD | simple_average_ensemble | -1.1006 | 0.0174 | 0.0254 | 9 | -0.0012 | 0.0251 | 0.0440 |
| GLD | validation_weighted_ensemble | -1.1006 | 0.0174 | 0.0254 | 9 | -0.0012 | 0.0251 | 0.0440 |
| GLD | ewma_tuned | -1.0823 | 0.0324 | 0.0450 | 11 | -0.0178 | 0.0081 | 0.0266 |
| GLD | ewma_094 | -1.0736 | 0.0382 | 0.0517 | 12 | -0.0257 | 0.0000 | 0.0184 |
| GLD | garch_11 | -1.0542 | 0.0493 | 0.0629 | 13 | -0.0433 | -0.0181 | 0.0000 |
| GLD | gjr_garch | -1.0504 | 0.0506 | 0.0655 | 14 | -0.0467 | -0.0216 | -0.0035 |
| GLD | rolling_63 | -0.9746 | 0.0860 | 0.1108 | 15 | -0.1155 | -0.0922 | -0.0755 |
| IWM | har_rolling_update | 0.4804 | 0.0216 | 0.0317 | 1 | 0.0061 | 0.0593 | 0.1013 |
| IWM | gjr_rolling_update | 0.4805 | 0.0209 | 0.0318 | 2 | 0.0060 | 0.0592 | 0.1012 |
| IWM | garch_rolling_update | 0.4805 | 0.0208 | 0.0320 | 3 | 0.0059 | 0.0591 | 0.1011 |
| IWM | ewma_rolling_update | 0.4806 | 0.0211 | 0.0318 | 4 | 0.0059 | 0.0591 | 0.1011 |
| IWM | previous_day_rv | 0.4834 | 0.0275 | 0.0440 | 5 | 0.0000 | 0.0535 | 0.0958 |
| IWM | rolling_21 | 0.4834 | 0.0275 | 0.0440 | 5 | 0.0000 | 0.0535 | 0.0958 |
| IWM | simple_average_ensemble | 0.4841 | 0.0341 | 0.0464 | 7 | -0.0014 | 0.0522 | 0.0945 |
| IWM | validation_weighted_ensemble | 0.4841 | 0.0341 | 0.0464 | 7 | -0.0014 | 0.0522 | 0.0945 |
| IWM | random_forest | 0.4843 | 0.0336 | 0.0508 | 9 | -0.0020 | 0.0517 | 0.0940 |
| IWM | hist_gradient_boosting | 0.4851 | 0.0376 | 0.0562 | 10 | -0.0035 | 0.0502 | 0.0927 |
| IWM | ewma_tuned | 0.5007 | 0.0628 | 0.0808 | 11 | -0.0357 | 0.0197 | 0.0635 |
| IWM | ewma_094 | 0.5107 | 0.0727 | 0.0922 | 12 | -0.0566 | 0.0000 | 0.0447 |
| IWM | gjr_garch | 0.5129 | 0.0828 | 0.1063 | 13 | -0.0610 | -0.0042 | 0.0406 |
| IWM | garch_11 | 0.5346 | 0.1056 | 0.1366 | 14 | -0.1060 | -0.0468 | 0.0000 |
| IWM | rolling_63 | 0.6037 | 0.1555 | 0.1941 | 15 | -0.2488 | -0.1819 | -0.1291 |
| JPM | har_rolling_update | 0.4714 | 0.0214 | 0.0296 | 1 | 0.0053 | 0.0370 | 0.0626 |
| JPM | garch_rolling_update | 0.4714 | 0.0192 | 0.0292 | 2 | 0.0053 | 0.0370 | 0.0626 |
| JPM | gjr_rolling_update | 0.4714 | 0.0202 | 0.0294 | 3 | 0.0052 | 0.0369 | 0.0625 |
| JPM | ewma_rolling_update | 0.4714 | 0.0196 | 0.0292 | 4 | 0.0052 | 0.0369 | 0.0625 |
| JPM | previous_day_rv | 0.4739 | 0.0263 | 0.0416 | 5 | 0.0000 | 0.0319 | 0.0576 |
| JPM | rolling_21 | 0.4739 | 0.0263 | 0.0416 | 5 | 0.0000 | 0.0319 | 0.0576 |
| JPM | simple_average_ensemble | 0.4744 | 0.0322 | 0.0446 | 7 | -0.0010 | 0.0309 | 0.0567 |
| JPM | validation_weighted_ensemble | 0.4744 | 0.0322 | 0.0446 | 7 | -0.0010 | 0.0309 | 0.0567 |
| JPM | random_forest | 0.4781 | 0.0418 | 0.0695 | 9 | -0.0089 | 0.0233 | 0.0493 |
| JPM | hist_gradient_boosting | 0.4789 | 0.0442 | 0.0719 | 10 | -0.0106 | 0.0216 | 0.0476 |
| JPM | ewma_tuned | 0.4871 | 0.0600 | 0.0794 | 11 | -0.0279 | 0.0049 | 0.0313 |
| JPM | ewma_094 | 0.4895 | 0.0608 | 0.0798 | 12 | -0.0329 | 0.0000 | 0.0266 |
| JPM | garch_11 | 0.5029 | 0.0796 | 0.1061 | 13 | -0.0611 | -0.0273 | 0.0000 |
| JPM | gjr_garch | 0.5048 | 0.0868 | 0.1120 | 14 | -0.0653 | -0.0313 | -0.0039 |
| JPM | rolling_63 | 0.5472 | 0.1275 | 0.1621 | 15 | -0.1547 | -0.1179 | -0.0882 |
| MSFT | har_rolling_update | 0.3538 | 0.0214 | 0.0318 | 1 | 0.0079 | 0.0505 | 0.1476 |
| MSFT | ewma_rolling_update | 0.3539 | 0.0204 | 0.0317 | 2 | 0.0076 | 0.0503 | 0.1475 |
| MSFT | gjr_rolling_update | 0.3540 | 0.0202 | 0.0318 | 3 | 0.0075 | 0.0502 | 0.1473 |
| MSFT | garch_rolling_update | 0.3540 | 0.0200 | 0.0318 | 4 | 0.0075 | 0.0501 | 0.1473 |
| MSFT | previous_day_rv | 0.3566 | 0.0261 | 0.0437 | 5 | 0.0000 | 0.0430 | 0.1409 |
| MSFT | rolling_21 | 0.3566 | 0.0261 | 0.0437 | 5 | 0.0000 | 0.0430 | 0.1409 |
| MSFT | simple_average_ensemble | 0.3590 | 0.0370 | 0.0509 | 7 | -0.0067 | 0.0366 | 0.1352 |
| MSFT | validation_weighted_ensemble | 0.3590 | 0.0370 | 0.0509 | 7 | -0.0067 | 0.0366 | 0.1352 |
| MSFT | random_forest | 0.3635 | 0.0460 | 0.0809 | 9 | -0.0193 | 0.0245 | 0.1243 |
| MSFT | hist_gradient_boosting | 0.3652 | 0.0479 | 0.0813 | 10 | -0.0241 | 0.0199 | 0.1202 |
| MSFT | ewma_tuned | 0.3692 | 0.0590 | 0.0783 | 11 | -0.0352 | 0.0093 | 0.1106 |
| MSFT | ewma_094 | 0.3727 | 0.0652 | 0.0844 | 12 | -0.0449 | 0.0000 | 0.1023 |
| MSFT | gjr_garch | 0.4102 | 0.1010 | 0.1273 | 13 | -0.1503 | -0.1008 | 0.0117 |
| MSFT | garch_11 | 0.4151 | 0.1054 | 0.1348 | 14 | -0.1640 | -0.1139 | 0.0000 |
| MSFT | rolling_63 | 0.4337 | 0.1331 | 0.1687 | 15 | -0.2162 | -0.1639 | -0.0449 |
| NVDA | gjr_rolling_update | 0.9636 | 0.0251 | 0.0352 | 1 | 0.0030 | 0.0187 | 0.0367 |
| NVDA | garch_rolling_update | 0.9637 | 0.0252 | 0.0354 | 2 | 0.0030 | 0.0187 | 0.0367 |
| NVDA | har_rolling_update | 0.9637 | 0.0257 | 0.0353 | 3 | 0.0030 | 0.0187 | 0.0367 |
| NVDA | ewma_rolling_update | 0.9637 | 0.0247 | 0.0353 | 4 | 0.0030 | 0.0187 | 0.0367 |
| NVDA | previous_day_rv | 0.9666 | 0.0327 | 0.0508 | 5 | 0.0000 | 0.0157 | 0.0338 |
| NVDA | rolling_21 | 0.9666 | 0.0327 | 0.0508 | 5 | 0.0000 | 0.0157 | 0.0338 |
| NVDA | simple_average_ensemble | 0.9669 | 0.0398 | 0.0513 | 7 | -0.0003 | 0.0154 | 0.0335 |
| NVDA | validation_weighted_ensemble | 0.9669 | 0.0398 | 0.0513 | 7 | -0.0003 | 0.0154 | 0.0335 |
| NVDA | random_forest | 0.9680 | 0.0415 | 0.0651 | 9 | -0.0015 | 0.0143 | 0.0324 |
| NVDA | hist_gradient_boosting | 0.9687 | 0.0443 | 0.0681 | 10 | -0.0022 | 0.0136 | 0.0317 |
| NVDA | ewma_tuned | 0.9785 | 0.0716 | 0.0910 | 11 | -0.0124 | 0.0036 | 0.0218 |
| NVDA | ewma_094 | 0.9820 | 0.0775 | 0.0972 | 12 | -0.0160 | 0.0000 | 0.0183 |
| NVDA | gjr_garch | 0.9932 | 0.0978 | 0.1193 | 13 | -0.0276 | -0.0114 | 0.0071 |
| NVDA | garch_11 | 1.0004 | 0.1096 | 0.1353 | 14 | -0.0350 | -0.0187 | 0.0000 |
| NVDA | rolling_63 | 1.0289 | 0.1480 | 0.1844 | 15 | -0.0645 | -0.0477 | -0.0285 |
| QQQ | har_rolling_update | 0.4409 | 0.0212 | 0.0318 | 1 | 0.0064 | 0.0456 | 0.0676 |
| QQQ | gjr_rolling_update | 0.4410 | 0.0208 | 0.0319 | 2 | 0.0062 | 0.0453 | 0.0673 |
| QQQ | garch_rolling_update | 0.4410 | 0.0207 | 0.0319 | 3 | 0.0061 | 0.0453 | 0.0673 |
| QQQ | ewma_rolling_update | 0.4411 | 0.0206 | 0.0319 | 4 | 0.0060 | 0.0451 | 0.0672 |
| QQQ | simple_average_ensemble | 0.4433 | 0.0327 | 0.0454 | 5 | 0.0009 | 0.0403 | 0.0624 |
| QQQ | validation_weighted_ensemble | 0.4433 | 0.0327 | 0.0454 | 5 | 0.0009 | 0.0403 | 0.0624 |
| QQQ | previous_day_rv | 0.4437 | 0.0273 | 0.0437 | 7 | 0.0000 | 0.0394 | 0.0615 |
| QQQ | rolling_21 | 0.4437 | 0.0273 | 0.0437 | 7 | 0.0000 | 0.0394 | 0.0615 |
| QQQ | random_forest | 0.4466 | 0.0391 | 0.0676 | 9 | -0.0065 | 0.0331 | 0.0554 |
| QQQ | hist_gradient_boosting | 0.4481 | 0.0446 | 0.0765 | 10 | -0.0100 | 0.0298 | 0.0522 |
| QQQ | ewma_tuned | 0.4565 | 0.0621 | 0.0830 | 11 | -0.0288 | 0.0118 | 0.0345 |
| QQQ | ewma_094 | 0.4619 | 0.0665 | 0.0862 | 12 | -0.0410 | 0.0000 | 0.0230 |
| QQQ | gjr_garch | 0.4687 | 0.0805 | 0.1046 | 13 | -0.0563 | -0.0147 | 0.0087 |
| QQQ | garch_11 | 0.4728 | 0.0865 | 0.1132 | 14 | -0.0656 | -0.0236 | 0.0000 |
| QQQ | rolling_63 | 0.5331 | 0.1364 | 0.1772 | 15 | -0.2015 | -0.1541 | -0.1275 |
| SPY | har_rolling_update | 0.3314 | 0.0206 | 0.0306 | 1 | 0.0080 | 0.0664 | 0.0962 |
| SPY | gjr_rolling_update | 0.3315 | 0.0193 | 0.0306 | 2 | 0.0080 | 0.0663 | 0.0961 |
| SPY | garch_rolling_update | 0.3315 | 0.0191 | 0.0306 | 3 | 0.0079 | 0.0663 | 0.0961 |
| SPY | ewma_rolling_update | 0.3315 | 0.0196 | 0.0305 | 4 | 0.0079 | 0.0662 | 0.0961 |
| SPY | previous_day_rv | 0.3341 | 0.0256 | 0.0418 | 5 | 0.0000 | 0.0588 | 0.0889 |
| SPY | rolling_21 | 0.3341 | 0.0256 | 0.0418 | 5 | 0.0000 | 0.0588 | 0.0889 |
| SPY | simple_average_ensemble | 0.3361 | 0.0396 | 0.0578 | 7 | -0.0060 | 0.0532 | 0.0834 |
| SPY | validation_weighted_ensemble | 0.3361 | 0.0396 | 0.0578 | 7 | -0.0060 | 0.0532 | 0.0834 |
| SPY | ewma_tuned | 0.3486 | 0.0618 | 0.0826 | 9 | -0.0434 | 0.0179 | 0.0493 |
| SPY | ewma_094 | 0.3550 | 0.0676 | 0.0864 | 10 | -0.0625 | 0.0000 | 0.0319 |
| SPY | gjr_garch | 0.3662 | 0.0836 | 0.1128 | 11 | -0.0959 | -0.0314 | 0.0015 |
| SPY | garch_11 | 0.3667 | 0.0821 | 0.1119 | 12 | -0.0975 | -0.0330 | 0.0000 |
| SPY | random_forest | 0.3759 | 0.0903 | 0.1538 | 13 | -0.1249 | -0.0588 | -0.0250 |
| SPY | hist_gradient_boosting | 0.3819 | 0.0979 | 0.1614 | 14 | -0.1431 | -0.0759 | -0.0415 |
| SPY | rolling_63 | 0.4381 | 0.1388 | 0.1791 | 15 | -0.3112 | -0.2341 | -0.1947 |

## Interpretation

The aggregate table reports average ranks across the full fixed universe rather than a selected subset of assets.
Where machine-learning models win, the likely driver is their use of volatility-of-volatility, market proxy and drawdown features.
Where simpler models win, the result is retained because volatility forecasting is noisy and regime-dependent.

## Failure Modes Observed

- GARCH-family forecasts can be unstable when a series has abrupt volatility regime shifts.
- Tree models may under-react to newly emerging stress regimes that are not represented in training data.
- Range-based features improve responsiveness but can amplify noisy high-low observations.

## Reproducibility

Run `python examples/run_forecasting_pipeline.py` to regenerate forecasts and `python examples/generate_all_reports.py` to refresh this report.
