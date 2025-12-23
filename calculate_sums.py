from fractions import Fraction

def binomial_coeff(n, k):
    if k < 0 or k > n:
        return 0
    res = 1
    for i in range(k):
        res = res * (n - i) // (i + 1)
    return res

def get_bernoulli_numbers(m):
    # Calculate Bernoulli numbers B_0 to B_m
    # Using recursive formula: sum_{k=0}^n C(n+1, k) * B_k = 0
    B = [Fraction(1, 1)]
    for n in range(1, m + 1):
        # sum_{k=0}^{n-1} C(n+1, k) * B_k + C(n+1, n) * B_n = 0
        # (n+1) * B_n = - sum_{k=0}^{n-1} C(n+1, k) * B_k
        s = Fraction(0)
        for k in range(n):
            s += binomial_coeff(n + 1, k) * B[k]
        bn = -s / (n + 1)
        B.append(bn)
    return B

def generate_sum_formula(p):
    # Sum_{k=1}^{n-1} k^p
    # Formula: 1/(p+1) * sum_{j=0}^p C(p+1, j) * B_j * n^{p+1-j}
    # Note: This formula is for sum_{k=0}^{n-1} k^p which is the same as sum_{k=1}^{n-1} k^p since 0^p = 0 for p>=1.
    
    B = get_bernoulli_numbers(p)
    coeffs = {} # power -> coefficient
    
    for j in range(p + 1):
        # term: n^{p+1-j}
        power = p + 1 - j
        coeff = Fraction(1, p + 1) * binomial_coeff(p + 1, j) * B[j]
        if coeff != 0:
            coeffs[power] = coeff
            
    return coeffs

def format_formula(p, coeffs):
    # Format as latex string
    # \Sigma^{p} =\sum_{k=1}^{n-1} k^p = ...
    terms = []
    sorted_powers = sorted(coeffs.keys(), reverse=True)
    
    for power in sorted_powers:
        coeff = coeffs[power]
        sign = "+" if coeff > 0 else "-"
        abs_coeff = abs(coeff)
        
        if abs_coeff.denominator == 1:
            c_str = str(abs_coeff.numerator) if abs_coeff.numerator != 1 else ""
        else:
            c_str = f"\\frac{{{abs_coeff.numerator}}}{{{abs_coeff.denominator}}}"
            
        if power == 1:
            p_str = "n"
        else:
            p_str = f"n^{{{power}}}"
            
        # Combine
        if c_str == "":
            term = p_str
        elif abs_coeff.denominator != 1:
             # \frac{n^k}{d} style usually preferred if numerator is 1
             if abs_coeff.numerator == 1:
                 term = f"\\frac{{{p_str}}}{{{abs_coeff.denominator}}}"
             else:
                 term = f"\\frac{{{abs_coeff.numerator}{p_str}}}{{{abs_coeff.denominator}}}"
        else:
            term = f"{c_str}{p_str}"
            
        terms.append((sign, term))
        
    # Join terms
    res = ""
    for i, (sign, term) in enumerate(terms):
        if i == 0:
            if sign == "-":
                res += "-" + term
            else:
                res += term
        else:
            res += sign + term
            
    return f"\\Sigma^{{{p}}} =\\sum_{{k=1}}^{{n-1}} k^{p} = {res}"

if __name__ == "__main__":
    for p in range(1, 11):
        coeffs = generate_sum_formula(p)
        print(format_formula(p, coeffs))
