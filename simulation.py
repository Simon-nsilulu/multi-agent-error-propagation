"""Статистическая иллюстрация (раздел 8, табл. 1).

Обобщённая медианная схема (7), n = 5 агентов, m = 0 фантомов,
10 000 испытаний в каждом из четырёх сценариев ошибок, seed = 2026.

Для каждого испытания вычисляются:
  * фактическое изменение |pi(s) - pi(r)|;
  * минимальная по i правая часть оценки (8);
  * тривиальная оценка (9): ||e||_inf;
  * итоговая оценка (11): min((8), (9));
и проверяется оценка (8) для каждого агента i (50 000 проверок на сценарий).

Запуск:  python simulation.py
Результат: results/table1.csv и вывод в консоль.
"""
import csv
import os

import numpy as np

SEED = 2026
N_TRIALS = 10_000
N_AGENTS = 5
TOL = 1e-12

SCENARIOS = {
    1: "Ошибается только первый агент, e1 ~ U[-1, 1]",
    2: "Независимые ошибки N(0; 0,05^2)",
    3: "Коррелированные ошибки (общий фактор, корреляция ~0,8, ст. откл. 0,05)",
    4: "Общее смещение +0,1 и шум N(0; 0,02^2)",
}


def errors(rng, scenario, n):
    """Ошибки агентов e = s - r для заданного сценария."""
    if scenario == 1:
        e = np.zeros(n)
        e[0] = rng.uniform(-1.0, 1.0)
        return e
    if scenario == 2:
        return rng.normal(0.0, 0.05, n)
    if scenario == 3:
        z = rng.normal()  # общий фактор: corr = 0,8, ст. откл. = 0,05
        return 0.05 * (np.sqrt(0.8) * z + np.sqrt(0.2) * rng.normal(size=n))
    if scenario == 4:
        return 0.1 + rng.normal(0.0, 0.02, n)
    raise ValueError(scenario)


def corridor_length(s, i, phantoms=()):
    """d_i = w_(q) - w_(q-1) по значениям (s_{-i}, a)."""
    w = sorted([s[j] for j in range(len(s)) if j != i] + list(phantoms))
    q = (len(s) + len(phantoms) + 1) // 2
    return w[q - 1] - w[q - 2]


def bound8(s, e, i, phantoms=()):
    """Правая часть оценки (8) для агента i."""
    others = [abs(e[j]) for j in range(len(e)) if j != i]
    return min(abs(e[i]), corridor_length(s, i, phantoms)) + max(others, default=0.0)


def run(seed=SEED, n_trials=N_TRIALS, n=N_AGENTS):
    rng = np.random.default_rng(seed)
    rows = []
    for sc in SCENARIOS:
        delta, b8, b9, b11 = [], [], [], []
        violations8 = violations11 = checks = exact = strict = 0
        for _ in range(n_trials):
            r = rng.uniform(0.0, 1.0, n)
            e = errors(rng, sc, n)
            s = r + e  # A_i = R: сообщения не усекаются
            d = abs(np.median(s) - np.median(r))
            per_agent = [bound8(s, e, i) for i in range(n)]
            checks += n
            violations8 += sum(d > b + TOL for b in per_agent)
            m8 = min(per_agent)
            m9 = float(np.max(np.abs(e)))
            m11 = min(m8, m9)
            violations11 += d > m11 + TOL
            exact += abs(d - m8) <= TOL
            strict += m8 < m9 - TOL
            delta.append(d); b8.append(m8); b9.append(m9); b11.append(m11)
        rows.append({
            "scenario": sc,
            "description": SCENARIOS[sc],
            "mean_delta": np.mean(delta),
            "mean_bound8": np.mean(b8),
            "mean_bound9": np.mean(b9),
            "mean_bound11": np.mean(b11),
            "share_8_stricter_than_9": strict / n_trials,
            "share_bound8_attained": exact / n_trials,
            "checks_bound8": checks,
            "violations_bound8": violations8,
            "violations_bound11": violations11,
        })
    return rows


if __name__ == "__main__":
    rows = run()
    os.makedirs("results", exist_ok=True)
    with open("results/table1.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    for r in rows:
        print(f"Сценарий {r['scenario']}: |pi(s)-pi(r)|={r['mean_delta']:.3f}  "
              f"(8)={r['mean_bound8']:.3f}  (9)={r['mean_bound9']:.3f}  "
              f"(11)={r['mean_bound11']:.3f}  (8) строже (9): {100*r['share_8_stricter_than_9']:.1f}%  "
              f"(8) достигается: {100*r['share_bound8_attained']:.1f}%  "
              f"нарушений (8): {r['violations_bound8']}/{r['checks_bound8']}  "
              f"нарушений (11): {r['violations_bound11']}")
