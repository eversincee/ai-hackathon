#include "diagnostics.h"
#include <math.h>
#include <string.h>

/* Minimum std used when calibration data is near-constant.
   Chosen so that a change of 0.1 on a signal of ~50 is treated as
   normal (< K_RATE * MIN_STD = 5 * 0.05 = 0.25). */
#define DIAG_MIN_STD 0.05

void diag_init(DiagChannel *ch) {
    memset(ch, 0, sizeof(DiagChannel));
}

int diag_process(DiagChannel *ch, double value) {
    /* --- Фаза калибровки --- */
    if (!ch->calibrated) {
        /* Отбрасывание выбросов: ждём не менее 30 отсчётов для устойчивой
           оценки статистики, затем отбрасываем явные выбросы. */
        if (ch->calib_count >= 30) {
            double std_est = (ch->calib_m2 > 0.0)
                             ? sqrt(ch->calib_m2 / (double)ch->calib_count)
                             : 0.0;
            if (std_est <= 0.0) {
                /* Constant signal so far: reject anything noticeably different */
                if (fabs(value - ch->calib_mean) > 1e-6) {
                    ch->prev_value = value;
                    ch->has_prev = 1;
                    return DIAG_FLAG_GOOD;
                }
            } else if (fabs(value - ch->calib_mean) > DIAG_CALIB_OUTLIER * std_est) {
                ch->prev_value = value;
                ch->has_prev = 1;
                return DIAG_FLAG_GOOD;
            }
        }

        /* Welford update */
        ch->calib_count++;
        {
            double delta  = value - ch->calib_mean;
            double delta2;
            ch->calib_mean += delta / (double)ch->calib_count;
            delta2 = value - ch->calib_mean;
            ch->calib_m2  += delta * delta2;
        }

        ch->window[ch->win_idx] = (float)value;
        ch->win_idx = (ch->win_idx + 1) % DIAG_WINDOW;
        /* Track window fill during calibration too */
        if (!ch->win_full && ch->win_idx == 0) ch->win_full = 1;
        ch->prev_value = value;
        ch->has_prev   = 1;

        if (ch->calib_count >= DIAG_CALIB_SAMPLES) {
            ch->calibrated = 1;
            ch->calib_std  = (ch->calib_m2 > 0.0)
                             ? sqrt(ch->calib_m2 / (double)ch->calib_count)
                             : 0.0;
            /* Apply minimum std floor so relative-threshold detectors work
               sensibly even when calibration data was near-constant. */
            if (ch->calib_std < DIAG_MIN_STD) {
                ch->calib_std = DIAG_MIN_STD;
            }
            ch->ewma      = ch->calib_mean;
            ch->ref_mean  = ch->calib_mean;
            ch->cusum_pos = 0.0;
            ch->cusum_neg = 0.0;
        }
        return DIAG_FLAG_GOOD;
    }

    /* --- Фаза детектирования --- */
    {
        int flag = DIAG_FLAG_GOOD;

        /* Детектор 1: темп (rate-of-change) -> Bad */
        if (ch->has_prev) {
            double delta = fabs(value - ch->prev_value);
            if (delta > DIAG_K_RATE * ch->calib_std) {
                flag = DIAG_FLAG_BAD;
            }
        }
        ch->prev_value = value;
        ch->has_prev   = 1;

        /* Детектор 2: скользящая дисперсия (EWMA) -> Bad
           EWMA оценки дисперсии позволяет «запомнить» недавнюю активность
           сигнала: после устранения смещения var_ewma затухает медленно,
           не вызывая ложного срабатывания «залипания» на восстановление. */
        ch->window[ch->win_idx] = (float)value;
        ch->win_idx = (ch->win_idx + 1) % DIAG_WINDOW;
        if (!ch->win_full && ch->win_idx == 0) ch->win_full = 1;

        if (ch->win_full && ch->calib_std > 1e-9) {
            double sum = 0.0, sum2 = 0.0;
            int wi;
            for (wi = 0; wi < DIAG_WINDOW; wi++) {
                sum  += (double)ch->window[wi];
                sum2 += (double)ch->window[wi] * (double)ch->window[wi];
            }
            {
                double wmean = sum / (double)DIAG_WINDOW;
                double var   = sum2 / (double)DIAG_WINDOW - wmean * wmean;
                ch->var_ewma = DIAG_ALPHA_VAR * var
                               + (1.0 - DIAG_ALPHA_VAR) * ch->var_ewma;
            }
            if (flag == DIAG_FLAG_GOOD) {
                double std2 = ch->calib_std * ch->calib_std;
                if (ch->var_ewma < DIAG_K_FROZEN * std2
                    || ch->var_ewma > DIAG_K_NOISE * std2) {
                    flag = DIAG_FLAG_BAD;
                }
            }
        }

        /* Обновляем адаптивное опорное среднее (очень медленно, ~40 сек).
           Следит за долгосрочным изменением рабочей точки ГТД,
           не успевает за реальными отказами датчика. */
        ch->ref_mean = DIAG_ALPHA_REF * value + (1.0 - DIAG_ALPHA_REF) * ch->ref_mean;

        /* Детектор 3: CUSUM с затуханием -> Potential
           Сравниваем с ref_mean (а не calib_mean), чтобы не реагировать
           на нормальный прогрев и изменение режима ГТД. */
        if (flag == DIAG_FLAG_GOOD && ch->calib_std > 1e-9) {
            double slack     = 0.5 * ch->calib_std;
            double threshold = DIAG_K_CUSUM * ch->calib_std;
            double diff      = value - ch->ref_mean;
            ch->cusum_pos = ch->cusum_pos * DIAG_CUSUM_DECAY + (diff - slack);
            ch->cusum_neg = ch->cusum_neg * DIAG_CUSUM_DECAY + (slack - diff);
            if (ch->cusum_pos < 0.0) ch->cusum_pos = 0.0;
            if (ch->cusum_neg < 0.0) ch->cusum_neg = 0.0;
            if (ch->cusum_pos > threshold || ch->cusum_neg > threshold) {
                flag = DIAG_FLAG_POTENTIAL;
            }
        }

        /* Детектор 4: EWMA -> Potential
           Сравниваем быстрый EWMA с медленным ref_mean.
           Реагирует на быстрый дрейф/скачок, игнорирует долгосрочный режим. */
        if (ch->calib_std > 1e-9) {
            ch->ewma = DIAG_ALPHA * value + (1.0 - DIAG_ALPHA) * ch->ewma;
            if (flag == DIAG_FLAG_GOOD &&
                fabs(ch->ewma - ch->ref_mean) > DIAG_K_EWMA * ch->calib_std) {
                flag = DIAG_FLAG_POTENTIAL;
            }
        }

        return flag;
    }
}
