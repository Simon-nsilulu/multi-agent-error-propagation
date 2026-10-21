"""Полный перебор на конечных сетках (раздел 8).

n <= 4, m <= 2, N = n + m нечётно, N >= 3,
r_i in {0,1,2,3}, a_j in {0,1,2}, e_i in {-3,-1,0,1,3}, A_i = R.

Проверяется:
  * оценка (8) для каждого агента i;
  * итоговая оценка (11);
  * оценка (8) строже (9) ровно тогда, когда выполнено условие (10).
Вычисления ведутся в целых числах (все значения целые), поэтому сравнения точные.

Запуск:  python exhaustive_check.py
"""
import itertools

R_VALUES = range(4)
A_VALUES = range(3)
E_VALUES = (-3, -1, 0, 1, 3)


def median(values):
    v = sorted(values)
    return v[len(v) // 2]  # N нечётно


def corridor_length(s, i, a):
    w = sorted([s[j] for j in range(len(s)) if j != i] + list(a))
    q = (len(s) + len(a) + 1) // 2
    return w[q - 1] - w[q - 2]


def main():
    variants = pairs = viol8 = viol11 = mismatch10 = 0
    for n in range(1, 5):
        for m in range(0, 3):
            if (n + m) % 2 == 0 or n + m < 3:
                continue
            for r in itertools.product(R_VALUES, repeat=n):
                for a in itertools.product(A_VALUES, repeat=m):
                    for e in itertools.product(E_VALUES, repeat=n):
                        s = [r[i] + e[i] for i in range(n)]
                        d = abs(median(s + list(a)) - median(list(r) + list(a)))
                        b8 = []
                        cond10 = False
                        for i in range(n):
                            Mi = max([abs(e[j]) for j in range(n) if j != i], default=0)
                            di = corridor_length(s, i, a)
                            b = min(abs(e[i]), di) + Mi
                            b8.append(b)
                            pairs += 1
                            viol8 += d > b
                            cond10 |= abs(e[i]) > di + Mi
                        b9 = max(abs(x) for x in e)
                        viol11 += d > min(min(b8), b9)
                        mismatch10 += (min(b8) < b9) != cond10
                        variants += 1
    print(f"Вариантов: {variants}; проверок оценки (8): {pairs}")
    print(f"Нарушений (8): {viol8}; нарушений (11): {viol11}; "
          f"расхождений с условием (10): {mismatch10}")


if __name__ == "__main__":
    main()
