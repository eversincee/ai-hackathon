#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "diagnostics.h"

/* --- Максимальные размеры --- */
#define MAX_ROWS     40000
#define MAX_SENSORS  40
#define MAX_LINE     2048
#define MAX_TS_LEN   20
#define MAX_HDR_LEN  256

/* --- Статические буферы (не учитываются в лимите памяти) --- */
static char   g_timestamps[MAX_ROWS][MAX_TS_LEN];
static double g_data[MAX_ROWS][MAX_SENSORS];
static int    g_flags[MAX_ROWS][MAX_SENSORS];
static char   g_sensor_headers[MAX_SENSORS][MAX_HDR_LEN];
static int    g_num_rows    = 0;
static int    g_num_sensors = 0;

/* --- Статические структуры диагностики (учитываются: ~20 КБ) --- */
static DiagChannel g_channels[MAX_SENSORS];

/* Заменить запятую на точку в строке (для набора данных 3) */
static void fix_decimal(char *s) {
    while (*s) {
        if (*s == ',') *s = '.';
        s++;
    }
}

/* Обрезать trailing \r\n */
static void rtrim(char *s) {
    int len = (int)strlen(s);
    while (len > 0 && (s[len-1] == '\r' || s[len-1] == '\n' || s[len-1] == ' '))
        s[--len] = '\0';
}

static int load_csv(const char *path) {
    FILE *f = fopen(path, "rb");
    char line[MAX_LINE];
    int  row = 0;

    if (!f) {
        fprintf(stderr, "Error: cannot open '%s'\n", path);
        return -1;
    }

    /* --- Чтение заголовка --- */
    if (!fgets(line, sizeof(line), f)) {
        fclose(f);
        fprintf(stderr, "Error: empty file '%s'\n", path);
        return -1;
    }
    rtrim(line);

    /* Парсим имена датчиков из заголовка */
    {
        char tmp[MAX_LINE];
        char *tok;
        int   col = 0;
        strncpy(tmp, line, sizeof(tmp) - 1);
        tmp[sizeof(tmp)-1] = '\0';

        tok = strtok(tmp, ";");
        while (tok && col <= MAX_SENSORS) {
            if (col > 0) {
                strncpy(g_sensor_headers[col-1], tok, MAX_HDR_LEN - 1);
                g_sensor_headers[col-1][MAX_HDR_LEN-1] = '\0';
                g_num_sensors = col;
            }
            tok = strtok(NULL, ";");
            col++;
        }
    }

    /* --- Чтение строк данных --- */
    while (fgets(line, sizeof(line), f) && row < MAX_ROWS) {
        char *semi;
        char vals[MAX_LINE];
        char *tok;
        int   col = 0;
        int   ts_len;

        rtrim(line);
        if (line[0] == '\0') continue;

        semi = strchr(line, ';');
        if (!semi) continue;

        /* Timestamp */
        ts_len = (int)(semi - line);
        if (ts_len >= MAX_TS_LEN) ts_len = MAX_TS_LEN - 1;
        strncpy(g_timestamps[row], line, (size_t)ts_len);
        g_timestamps[row][ts_len] = '\0';

        /* Значения датчиков */
        strncpy(vals, semi + 1, sizeof(vals) - 1);
        vals[sizeof(vals)-1] = '\0';
        fix_decimal(vals);

        tok = strtok(vals, ";");
        while (tok && col < MAX_SENSORS) {
            char  *endptr;
            double v = strtod(tok, &endptr);
            g_data[row][col] = (endptr == tok) ? NAN : v;
            tok = strtok(NULL, ";");
            col++;
        }
        row++;
    }

    fclose(f);
    g_num_rows = row;
    return row;
}

/* Пишет один CSV-файл на один канал.
   Формат совпадает с примером выходного файла:
     - разделитель ;
     - CRLF строки (как в исходных файлах Windows)
     - кодировка CP1251 (заголовок берётся из входного файла as-is) */
static int write_channel_csv(const char *prefix, int sensor_idx) {
    char path[768];
    FILE *f;
    int   r;

    snprintf(path, sizeof(path), "%s_%02d.csv", prefix, sensor_idx + 1);
    f = fopen(path, "wb");
    if (!f) {
        fprintf(stderr, "Error: cannot write '%s'\n", path);
        return -1;
    }

    fprintf(f, "TimeStamp;%s;0 - Bad, 1 - Good, 2 - Potential\r\n",
            g_sensor_headers[sensor_idx]);

    for (r = 0; r < g_num_rows; r++) {
        fprintf(f, "%s;%.6g;%d\r\n",
                g_timestamps[r],
                g_data[r][sensor_idx],
                g_flags[r][sensor_idx]);
    }

    fclose(f);
    return 0;
}

static int write_all_channels(const char *prefix) {
    int s;
    for (s = 0; s < g_num_sensors; s++) {
        if (write_channel_csv(prefix, s) < 0) return -1;
    }
    return 0;
}

int main(int argc, char *argv[]) {
    int s, r;

    if (argc != 3) {
        fprintf(stderr,
                "Usage: %s <input.csv> <output_prefix>\n"
                "  Creates one CSV per channel: <output_prefix>_01.csv, _02.csv, ...\n",
                argv[0]);
        return 1;
    }

    printf("Loading '%s'...\n", argv[1]);
    if (load_csv(argv[1]) < 0) return 1;
    printf("Loaded %d rows, %d sensors.\n", g_num_rows, g_num_sensors);

    for (s = 0; s < g_num_sensors; s++) {
        diag_init(&g_channels[s]);
    }

    for (r = 0; r < g_num_rows; r++) {
        for (s = 0; s < g_num_sensors; s++) {
            double v = g_data[r][s];
            g_flags[r][s] = isnan(v) ? DIAG_FLAG_BAD : diag_process(&g_channels[s], v);
        }
    }

    printf("Writing %d channel files with prefix '%s'...\n",
           g_num_sensors, argv[2]);
    if (write_all_channels(argv[2]) < 0) return 1;
    printf("Done. Created %d files: %s_01.csv .. %s_%02d.csv\n",
           g_num_sensors, argv[2], argv[2], g_num_sensors);

    return 0;
}
