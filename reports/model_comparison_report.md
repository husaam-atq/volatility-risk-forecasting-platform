# Model Comparison Report

## Data Source

| data_source | raw_price_rows | first_date | last_date |
| --- | --- | --- | --- |
| yfinance | 28620 | 2015-01-02 00:00:00 | 2026-05-20 00:00:00 |

The fixed universe is evaluated as a complete panel; assets and periods are not selected based on model performance.

## Executive Summary

The modelling layer compares rolling realised-volatility baselines, EWMA, GARCH-family models, tree-based regressors and ensemble forecasts on identical out-of-sample dates.
QLIKE is treated as the primary metric because it is robust for volatility forecast comparison and penalises variance underestimation. The implementation uses the standard non-negative variance-ratio loss.

## Aggregate Test-Period Ranking

| model | asset_count | avg_qlike | avg_mae | avg_rmse | avg_rank | top_two_share | improvement_vs_rolling_21 | improvement_vs_ewma | improvement_vs_garch |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| har_rolling_update | 10 | 0.0056 | 0.0071 | 0.0128 | 1.8000 | 0.8000 | 0.4041 | 0.8315 | 0.9150 |
| garch_rolling_update | 10 | 0.0056 | 0.0066 | 0.0128 | 2.4000 | 0.5000 | 0.4010 | 0.8307 | 0.9145 |
| gjr_rolling_update | 10 | 0.0056 | 0.0065 | 0.0127 | 2.5000 | 0.6000 | 0.3979 | 0.8298 | 0.9138 |
| ewma_rolling_update | 10 | 0.0057 | 0.0066 | 0.0128 | 3.3000 | 0.1000 | 0.3938 | 0.8286 | 0.9135 |
| validation_weighted_ensemble | 10 | 0.0079 | 0.0104 | 0.0168 | 5.6000 | 0.0000 | 0.1656 | 0.7639 | 0.8815 |
| har_rv_market_huber | 10 | 0.0091 | 0.0092 | 0.0178 | 7.3000 | 0.0000 | 0.0128 | 0.7204 | 0.8586 |
| previous_day_rv | 10 | 0.0093 | 0.0087 | 0.0179 | 7.9000 | 0.0000 | 0.0000 | 0.7172 | 0.8567 |
| rolling_21 | 10 | 0.0093 | 0.0087 | 0.0179 | 7.9000 | 0.0000 | 0.0000 | 0.7172 | 0.8567 |
| har_rv_log_ridge | 10 | 0.0094 | 0.0101 | 0.0184 | 7.9000 | 0.0000 | -0.0126 | 0.7133 | 0.8562 |
| simple_average_ensemble | 10 | 0.0096 | 0.0121 | 0.0190 | 9.3000 | 0.0000 | -0.0281 | 0.7093 | 0.8547 |
| har_rv_market_log_ridge | 10 | 0.0097 | 0.0107 | 0.0186 | 9.1000 | 0.0000 | -0.0368 | 0.7065 | 0.8530 |
| random_forest | 10 | 0.0235 | 0.0152 | 0.0313 | 12.8000 | 0.0000 | -1.7601 | 0.2136 | 0.6103 |
| hist_gradient_boosting | 10 | 0.0269 | 0.0178 | 0.0339 | 13.6000 | 0.0000 | -2.1146 | 0.1121 | 0.5701 |
| ewma_tuned | 10 | 0.0293 | 0.0227 | 0.0326 | 13.8000 | 0.0000 | -2.1536 | 0.1073 | 0.5501 |
| ewma_094 | 10 | 0.0331 | 0.0238 | 0.0344 | 14.4000 | 0.0000 | -2.5678 | 0.0000 | 0.4881 |
| garch_11 | 10 | 0.0741 | 0.0383 | 0.0535 | 16.5000 | 0.0000 | -6.6866 | -1.1789 | 0.0000 |
| egarch_t | 10 | 0.0761 | 0.0381 | 0.0529 | 16.9000 | 0.0000 | -7.2392 | -1.3267 | -0.1267 |
| rolling_63 | 10 | 0.0999 | 0.0470 | 0.0657 | 17.8000 | 0.0000 | -9.9984 | -2.0768 | -0.6198 |
| gjr_garch | 10 | 0.1580 | 0.0495 | 0.0689 | 18.2000 | 0.0000 | -16.1720 | -3.6690 | -1.5115 |

## Asset-Level Test-Period Ranking

| asset | model | qlike | mae | rmse | rank_qlike | improvement_vs_rolling_21 | improvement_vs_ewma | improvement_vs_garch |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AAPL | gjr_rolling_update | 0.0067 | 0.0071 | 0.0140 | 1 | 0.4315 | 0.8258 | 0.9165 |
| AAPL | har_rolling_update | 0.0068 | 0.0077 | 0.0142 | 2 | 0.4199 | 0.8223 | 0.9148 |
| AAPL | garch_rolling_update | 0.0068 | 0.0076 | 0.0143 | 3 | 0.4194 | 0.8221 | 0.9147 |
| AAPL | ewma_rolling_update | 0.0070 | 0.0072 | 0.0143 | 4 | 0.4032 | 0.8171 | 0.9123 |
| AAPL | validation_weighted_ensemble | 0.0100 | 0.0116 | 0.0191 | 5 | 0.1545 | 0.7410 | 0.8758 |
| AAPL | har_rv_market_log_ridge | 0.0112 | 0.0105 | 0.0199 | 6 | 0.0498 | 0.7089 | 0.8604 |
| AAPL | har_rv_log_ridge | 0.0112 | 0.0104 | 0.0200 | 7 | 0.0493 | 0.7087 | 0.8604 |
| AAPL | simple_average_ensemble | 0.0112 | 0.0131 | 0.0207 | 8 | 0.0479 | 0.7083 | 0.8602 |
| AAPL | har_rv_market_huber | 0.0115 | 0.0095 | 0.0199 | 9 | 0.0263 | 0.7017 | 0.8570 |
| AAPL | previous_day_rv | 0.0118 | 0.0096 | 0.0205 | 10 | 0.0000 | 0.6936 | 0.8531 |
| AAPL | rolling_21 | 0.0118 | 0.0096 | 0.0205 | 10 | 0.0000 | 0.6936 | 0.8531 |
| AAPL | random_forest | 0.0205 | 0.0161 | 0.0384 | 12 | -0.7409 | 0.4666 | 0.7443 |
| AAPL | hist_gradient_boosting | 0.0224 | 0.0180 | 0.0414 | 13 | -0.9042 | 0.4166 | 0.7203 |
| AAPL | ewma_tuned | 0.0355 | 0.0262 | 0.0386 | 14 | -2.0116 | 0.0773 | 0.5576 |
| AAPL | ewma_094 | 0.0385 | 0.0276 | 0.0406 | 15 | -2.2640 | 0.0000 | 0.5206 |
| AAPL | egarch_t | 0.0704 | 0.0386 | 0.0550 | 16 | -4.9713 | -0.8294 | 0.1229 |
| AAPL | garch_11 | 0.0802 | 0.0429 | 0.0601 | 17 | -5.8082 | -1.0858 | 0.0000 |
| AAPL | rolling_63 | 0.1163 | 0.0558 | 0.0797 | 18 | -8.8716 | -2.0243 | -0.4500 |
| AAPL | gjr_garch | 0.1355 | 0.0522 | 0.0702 | 19 | -10.4979 | -2.5226 | -0.6888 |
| GLD | har_rolling_update | 0.0045 | 0.0045 | 0.0086 | 1 | 0.4434 | 0.8382 | 0.9252 |
| GLD | gjr_rolling_update | 0.0046 | 0.0046 | 0.0087 | 2 | 0.4329 | 0.8351 | 0.9238 |
| GLD | ewma_rolling_update | 0.0047 | 0.0045 | 0.0087 | 3 | 0.4277 | 0.8336 | 0.9231 |
| GLD | garch_rolling_update | 0.0047 | 0.0043 | 0.0088 | 4 | 0.4266 | 0.8333 | 0.9230 |
| GLD | validation_weighted_ensemble | 0.0056 | 0.0052 | 0.0099 | 5 | 0.3111 | 0.7997 | 0.9075 |
| GLD | previous_day_rv | 0.0081 | 0.0061 | 0.0119 | 6 | 0.0000 | 0.7093 | 0.8657 |
| GLD | rolling_21 | 0.0081 | 0.0061 | 0.0119 | 6 | 0.0000 | 0.7093 | 0.8657 |
| GLD | har_rv_market_huber | 0.0083 | 0.0065 | 0.0124 | 8 | -0.0149 | 0.7049 | 0.8637 |
| GLD | har_rv_market_log_ridge | 0.0084 | 0.0069 | 0.0127 | 9 | -0.0273 | 0.7013 | 0.8620 |
| GLD | simple_average_ensemble | 0.0088 | 0.0083 | 0.0150 | 10 | -0.0849 | 0.6846 | 0.8543 |
| GLD | har_rv_log_ridge | 0.0092 | 0.0085 | 0.0180 | 11 | -0.1296 | 0.6716 | 0.8483 |
| GLD | ewma_tuned | 0.0229 | 0.0144 | 0.0215 | 12 | -1.8131 | 0.1821 | 0.6222 |
| GLD | ewma_094 | 0.0280 | 0.0160 | 0.0241 | 13 | -2.4395 | 0.0000 | 0.5380 |
| GLD | gjr_garch | 0.0468 | 0.0215 | 0.0293 | 14 | -4.7433 | -0.6698 | 0.2286 |
| GLD | garch_11 | 0.0607 | 0.0236 | 0.0370 | 15 | -6.4451 | -1.1646 | 0.0000 |
| GLD | egarch_t | 0.0741 | 0.0264 | 0.0428 | 16 | -8.0900 | -1.6428 | -0.2209 |
| GLD | random_forest | 0.0769 | 0.0187 | 0.0496 | 17 | -8.4421 | -1.7452 | -0.2682 |
| GLD | hist_gradient_boosting | 0.0895 | 0.0199 | 0.0518 | 18 | -9.9880 | -2.1946 | -0.4759 |
| GLD | rolling_63 | 0.1014 | 0.0340 | 0.0493 | 19 | -11.4449 | -2.6182 | -0.6716 |
| IWM | ewma_rolling_update | 0.0042 | 0.0055 | 0.0094 | 1 | 0.4264 | 0.8317 | 0.8863 |
| IWM | har_rolling_update | 0.0042 | 0.0062 | 0.0096 | 2 | 0.4239 | 0.8309 | 0.8858 |
| IWM | garch_rolling_update | 0.0042 | 0.0053 | 0.0094 | 3 | 0.4229 | 0.8306 | 0.8856 |
| IWM | gjr_rolling_update | 0.0043 | 0.0050 | 0.0094 | 4 | 0.4168 | 0.8288 | 0.8844 |
| IWM | validation_weighted_ensemble | 0.0058 | 0.0072 | 0.0116 | 5 | 0.2100 | 0.7681 | 0.8434 |
| IWM | har_rv_market_huber | 0.0072 | 0.0076 | 0.0131 | 6 | 0.0246 | 0.7137 | 0.8066 |
| IWM | simple_average_ensemble | 0.0073 | 0.0087 | 0.0140 | 7 | 0.0097 | 0.7094 | 0.8037 |
| IWM | previous_day_rv | 0.0073 | 0.0072 | 0.0133 | 8 | 0.0000 | 0.7065 | 0.8017 |
| IWM | rolling_21 | 0.0073 | 0.0072 | 0.0133 | 8 | 0.0000 | 0.7065 | 0.8017 |
| IWM | har_rv_log_ridge | 0.0075 | 0.0082 | 0.0136 | 10 | -0.0191 | 0.7009 | 0.7979 |
| IWM | har_rv_market_log_ridge | 0.0078 | 0.0089 | 0.0143 | 11 | -0.0569 | 0.6898 | 0.7904 |
| IWM | hist_gradient_boosting | 0.0189 | 0.0137 | 0.0272 | 12 | -1.5809 | 0.2425 | 0.4883 |
| IWM | ewma_tuned | 0.0218 | 0.0173 | 0.0237 | 13 | -1.9703 | 0.1283 | 0.4111 |
| IWM | random_forest | 0.0233 | 0.0140 | 0.0300 | 14 | -2.1737 | 0.0686 | 0.3707 |
| IWM | ewma_094 | 0.0250 | 0.0187 | 0.0254 | 15 | -2.4073 | 0.0000 | 0.3244 |
| IWM | garch_11 | 0.0370 | 0.0219 | 0.0310 | 16 | -4.0436 | -0.4802 | 0.0000 |
| IWM | egarch_t | 0.0497 | 0.0246 | 0.0362 | 17 | -5.7662 | -0.9858 | -0.3416 |
| IWM | rolling_63 | 0.0809 | 0.0374 | 0.0495 | 18 | -10.0224 | -2.2349 | -1.1854 |
| IWM | gjr_garch | 0.1647 | 0.0404 | 0.0528 | 19 | -21.4447 | -5.5873 | -3.4502 |
| JPM | garch_rolling_update | 0.0081 | 0.0065 | 0.0138 | 1 | 0.3702 | 0.8314 | 0.9228 |
| JPM | gjr_rolling_update | 0.0081 | 0.0065 | 0.0138 | 2 | 0.3695 | 0.8312 | 0.9227 |
| JPM | har_rolling_update | 0.0081 | 0.0074 | 0.0139 | 3 | 0.3692 | 0.8311 | 0.9227 |
| JPM | ewma_rolling_update | 0.0082 | 0.0066 | 0.0138 | 4 | 0.3604 | 0.8287 | 0.9216 |
| JPM | validation_weighted_ensemble | 0.0112 | 0.0105 | 0.0175 | 5 | 0.1215 | 0.7648 | 0.8923 |
| JPM | har_rv_market_huber | 0.0125 | 0.0089 | 0.0188 | 6 | 0.0247 | 0.7389 | 0.8804 |
| JPM | har_rv_market_log_ridge | 0.0126 | 0.0101 | 0.0188 | 7 | 0.0126 | 0.7356 | 0.8789 |
| JPM | har_rv_log_ridge | 0.0126 | 0.0100 | 0.0188 | 8 | 0.0125 | 0.7356 | 0.8789 |
| JPM | previous_day_rv | 0.0128 | 0.0086 | 0.0194 | 9 | 0.0000 | 0.7322 | 0.8774 |
| JPM | rolling_21 | 0.0128 | 0.0086 | 0.0194 | 9 | 0.0000 | 0.7322 | 0.8774 |
| JPM | simple_average_ensemble | 0.0130 | 0.0123 | 0.0195 | 11 | -0.0148 | 0.7283 | 0.8756 |
| JPM | random_forest | 0.0148 | 0.0120 | 0.0227 | 12 | -0.1528 | 0.6913 | 0.8587 |
| JPM | hist_gradient_boosting | 0.0178 | 0.0157 | 0.0258 | 13 | -0.3870 | 0.6286 | 0.8299 |
| JPM | ewma_094 | 0.0478 | 0.0259 | 0.0376 | 14 | -2.7346 | 0.0000 | 0.5421 |
| JPM | ewma_tuned | 0.0483 | 0.0261 | 0.0379 | 15 | -2.7725 | -0.0101 | 0.5375 |
| JPM | garch_11 | 0.1044 | 0.0391 | 0.0552 | 16 | -7.1562 | -1.1840 | 0.0000 |
| JPM | egarch_t | 0.1184 | 0.0406 | 0.0572 | 17 | -8.2487 | -1.4765 | -0.1339 |
| JPM | rolling_63 | 0.1230 | 0.0487 | 0.0679 | 18 | -8.6140 | -1.5743 | -0.1787 |
| JPM | gjr_garch | 0.1726 | 0.0518 | 0.0733 | 19 | -12.4848 | -2.6108 | -0.6533 |
| MSFT | garch_rolling_update | 0.0071 | 0.0072 | 0.0137 | 1 | 0.3594 | 0.8093 | 0.9043 |
| MSFT | har_rolling_update | 0.0072 | 0.0074 | 0.0137 | 2 | 0.3533 | 0.8075 | 0.9034 |
| MSFT | ewma_rolling_update | 0.0073 | 0.0070 | 0.0137 | 3 | 0.3446 | 0.8049 | 0.9021 |
| MSFT | gjr_rolling_update | 0.0074 | 0.0074 | 0.0140 | 4 | 0.3335 | 0.8016 | 0.9004 |
| MSFT | validation_weighted_ensemble | 0.0094 | 0.0108 | 0.0170 | 5 | 0.1565 | 0.7489 | 0.8740 |
| MSFT | har_rv_market_huber | 0.0109 | 0.0095 | 0.0185 | 6 | 0.0226 | 0.7091 | 0.8540 |
| MSFT | previous_day_rv | 0.0111 | 0.0089 | 0.0188 | 7 | 0.0000 | 0.7024 | 0.8506 |
| MSFT | rolling_21 | 0.0111 | 0.0089 | 0.0188 | 7 | 0.0000 | 0.7024 | 0.8506 |
| MSFT | har_rv_market_log_ridge | 0.0113 | 0.0111 | 0.0189 | 9 | -0.0116 | 0.6989 | 0.8489 |
| MSFT | har_rv_log_ridge | 0.0114 | 0.0108 | 0.0188 | 10 | -0.0248 | 0.6950 | 0.8469 |
| MSFT | simple_average_ensemble | 0.0115 | 0.0132 | 0.0195 | 11 | -0.0300 | 0.6935 | 0.8462 |
| MSFT | random_forest | 0.0139 | 0.0139 | 0.0236 | 12 | -0.2457 | 0.6292 | 0.8139 |
| MSFT | hist_gradient_boosting | 0.0163 | 0.0154 | 0.0246 | 13 | -0.4679 | 0.5631 | 0.7807 |
| MSFT | ewma_tuned | 0.0356 | 0.0250 | 0.0345 | 14 | -2.1980 | 0.0482 | 0.5223 |
| MSFT | ewma_094 | 0.0374 | 0.0242 | 0.0343 | 15 | -2.3599 | 0.0000 | 0.4982 |
| MSFT | egarch_t | 0.0727 | 0.0385 | 0.0496 | 16 | -5.5321 | -0.9442 | 0.0244 |
| MSFT | garch_11 | 0.0745 | 0.0408 | 0.0538 | 17 | -5.6952 | -0.9927 | 0.0000 |
| MSFT | rolling_63 | 0.1013 | 0.0459 | 0.0624 | 18 | -8.1000 | -1.7085 | -0.3592 |
| MSFT | gjr_garch | 0.1677 | 0.0590 | 0.0813 | 19 | -14.0581 | -3.4818 | -1.2491 |
| NVDA | gjr_rolling_update | 0.0081 | 0.0127 | 0.0288 | 1 | 0.3553 | 0.8159 | 0.9562 |
| NVDA | har_rolling_update | 0.0081 | 0.0140 | 0.0291 | 2 | 0.3539 | 0.8155 | 0.9561 |
| NVDA | ewma_rolling_update | 0.0081 | 0.0132 | 0.0289 | 3 | 0.3489 | 0.8141 | 0.9558 |
| NVDA | garch_rolling_update | 0.0082 | 0.0131 | 0.0292 | 4 | 0.3464 | 0.8134 | 0.9556 |
| NVDA | previous_day_rv | 0.0125 | 0.0176 | 0.0405 | 5 | 0.0000 | 0.7145 | 0.9321 |
| NVDA | rolling_21 | 0.0125 | 0.0176 | 0.0405 | 5 | 0.0000 | 0.7145 | 0.9321 |
| NVDA | har_rv_market_huber | 0.0129 | 0.0192 | 0.0403 | 7 | -0.0313 | 0.7056 | 0.9300 |
| NVDA | har_rv_log_ridge | 0.0143 | 0.0220 | 0.0405 | 8 | -0.1417 | 0.6740 | 0.9225 |
| NVDA | validation_weighted_ensemble | 0.0146 | 0.0279 | 0.0431 | 9 | -0.1637 | 0.6677 | 0.9210 |
| NVDA | simple_average_ensemble | 0.0146 | 0.0279 | 0.0431 | 10 | -0.1637 | 0.6677 | 0.9210 |
| NVDA | har_rv_market_log_ridge | 0.0163 | 0.0264 | 0.0437 | 11 | -0.3047 | 0.6275 | 0.9114 |
| NVDA | random_forest | 0.0180 | 0.0284 | 0.0478 | 12 | -0.4418 | 0.5884 | 0.9021 |
| NVDA | hist_gradient_boosting | 0.0288 | 0.0389 | 0.0573 | 13 | -1.3037 | 0.3422 | 0.8435 |
| NVDA | ewma_tuned | 0.0372 | 0.0471 | 0.0683 | 14 | -1.9733 | 0.1511 | 0.7980 |
| NVDA | ewma_094 | 0.0438 | 0.0503 | 0.0723 | 15 | -2.5024 | 0.0000 | 0.7621 |
| NVDA | rolling_63 | 0.1135 | 0.0930 | 0.1272 | 16 | -8.0649 | -1.5882 | 0.3843 |
| NVDA | egarch_t | 0.1293 | 0.0949 | 0.1246 | 17 | -9.3337 | -1.9504 | 0.2981 |
| NVDA | garch_11 | 0.1843 | 0.1110 | 0.1499 | 18 | -13.7227 | -3.2036 | 0.0000 |
| NVDA | gjr_garch | 0.2111 | 0.1134 | 0.1542 | 19 | -15.8628 | -3.8146 | -0.1454 |
| QQQ | har_rolling_update | 0.0042 | 0.0060 | 0.0100 | 1 | 0.4500 | 0.8696 | 0.9088 |
| QQQ | garch_rolling_update | 0.0042 | 0.0057 | 0.0100 | 2 | 0.4474 | 0.8690 | 0.9083 |
| QQQ | gjr_rolling_update | 0.0042 | 0.0052 | 0.0098 | 3 | 0.4449 | 0.8684 | 0.9079 |
| QQQ | ewma_rolling_update | 0.0042 | 0.0055 | 0.0100 | 4 | 0.4405 | 0.8674 | 0.9072 |
| QQQ | validation_weighted_ensemble | 0.0059 | 0.0079 | 0.0125 | 5 | 0.2258 | 0.8165 | 0.8716 |
| QQQ | har_rv_market_huber | 0.0072 | 0.0076 | 0.0140 | 6 | 0.0477 | 0.7743 | 0.8420 |

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
