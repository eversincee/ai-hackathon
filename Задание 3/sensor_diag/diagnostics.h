#ifndef DIAGNOSTICS_H
#define DIAGNOSTICS_H

/* --- Размеры буферов --- */
#define DIAG_WINDOW         100    /* кольцевой буфер для скользящей дисперсии */
#define DIAG_CALIB_SAMPLES  250    /* отсчётов на калибровку (~5 сек при 50 Гц) */

/* --- Коэффициенты детекторов --- */
#define DIAG_ALPHA          0.05    /* скорость EWMA сигнала */
#define DIAG_ALPHA_VAR      0.05    /* скорость EWMA оценки дисперсии */
#define DIAG_ALPHA_REF      0.02    /* скорость адаптации опорного среднего (~50 тактов = ~1 сек) */
#define DIAG_K_RATE         5.0     /* порог темпового детектора (в std) */
#define DIAG_K_FROZEN       0.001   /* нижний порог дисперсии (доля std^2) */
#define DIAG_K_NOISE        10.0    /* верхний порог дисперсии (кратно std^2) */
#define DIAG_K_CUSUM        25.0    /* порог CUSUM (в std) */
#define DIAG_CUSUM_DECAY    0.9     /* коэффициент затухания CUSUM за один такт */
#define DIAG_K_EWMA         6.0     /* порог EWMA (в std) */
#define DIAG_CALIB_OUTLIER  3.0     /* порог отбрасывания выбросов при калибровке */

/* --- Флаги качества --- */
#define DIAG_FLAG_BAD       0
#define DIAG_FLAG_GOOD      1
#define DIAG_FLAG_POTENTIAL 2

/* --- Состояние одного канала --- */
typedef struct {
    /* Фаза */
    int    calibrated;
    int    calib_count;

    /* Калибровочная статистика (метод Welford) */
    double calib_mean;
    double calib_m2;
    double calib_std;

    /* EWMA сигнала и адаптивное опорное среднее */
    double ewma;
    double ref_mean;  /* медленно адаптируется к рабочей точке, α=DIAG_ALPHA_REF */

    /* CUSUM */
    double cusum_pos;
    double cusum_neg;

    /* Темп */
    double prev_value;
    int    has_prev;

    /* Скользящая дисперсия */
    float  window[DIAG_WINDOW];
    int    win_idx;
    int    win_full;
    double var_ewma;   /* EWMA оценки дисперсии скользящего окна */
} DiagChannel;

/* --- API --- */
void diag_init(DiagChannel *ch);
int  diag_process(DiagChannel *ch, double value);

#endif /* DIAGNOSTICS_H */
