
import re
from sympy import Symbol, sympify, Poly, latex, expand


def process_sums():
    # Read sums.txt
    try:
        with open('sums.txt', 'r', encoding='utf-16') as f:
            content = f.read()
    except:
        with open('sums.txt', 'r', encoding='utf-8') as f:
            content = f.read()

    lines = content.splitlines()
    
    n = Symbol('n')
    
    # Store results
    # Key: (p, q), Value: polynomial expression string
    db = {}
    
    current_cmd = ""
    for line in lines:
        line = line.strip()
        if not line: continue
        
        if line.startswith('>>>'):
            line = line[3:].strip()
            
        if 'expand(summation' in line:
            # Parse p and q
            # matches k**3*(n-k)**4 or k**3*(n-k)**3 or (n-k)**4*k**4
            # Normalize pattern matching
            # We assume form like k**P * (n-k)**Q or (n-k)**Q * k**P
            
            p_match = re.search(r'k\*\*(\d+)', line)
            q_match = re.search(r'\(n-k\)\*\*(\d+)', line)
            
            if p_match and q_match:
                p = int(p_match.group(1))
                q = int(q_match.group(1))
                # standardize key with p <= q to handle commutativity if needed, 
                # but user notation distinguishes \Sigma^{p,q} usually. 
                # Let's keep as p,q extracted.
                # In the file sums.txt, user seems to use consistent ordering in python command or varies it.
                # We will trust the order found or just use the pair.
                current_cmd = (p, q)
            else:
                current_cmd = None
        elif current_cmd:
            # Result line
            try:
                poly = sympify(line)
                db[current_cmd] = poly
                current_cmd = None
            except:
                pass
                
    # Now generate the markdown content
    # We want to output for n^8, n^9, etc.
    # We look for pairs (p, q) in the db.
    
    output = []
    
    # Sort keys by degree (p+q+1)
    sorted_keys = sorted(db.keys(), key=lambda x: x[0]+x[1])
    
    import math

    def factorial(x):
        return math.factorial(x)

    for p, q in sorted_keys:
        poly_expr = db[(p, q)]
        degree_val = p + q + 1
        
        # Calculate the leading coefficient expected: p!q! / (p+q+1)!
        # Wait, the integral of x^p(1-x)^q is p!q!/(p+q+1)!. 
        # Summation approximation is similar.
        # The term n^(p+q+1) has coeff 1 / (Factor).
        # Factor = (p+q+1)! / (p!q!).
        
        factor = factorial(p+q+1) // (factorial(p) * factorial(q))
        
        # Check if the leading term implies this factor
        poly = Poly(poly_expr, n)
        if poly.degree() != degree_val:
            # Skip if degree doesn't match expectation (might be incomplete data)
            continue
            
        leading_coeff = poly.coeff_monomial(n**degree_val)
        
        # We expect leading_coeff to be 1/factor approx?
        # 1/280 for 8!/(3!4!) = 40320 / (6*24) = 40320 / 144 = 280. Correct.
        
        # We want equation: n^{degree} = Factor * Sigma^{p,q} - Factor * (rest)
        # poly = 1/Factor * n^{degree} + rest
        # Factor * poly = n^{degree} + Factor * rest
        # n^{degree} = Factor * Sigma - Factor * rest
        # Note: Sigma in LHS of equation in npower.md is actually the Summation value?
        # No, in npower.md: n^7 = ... + Factor * Sigma
        # So LHS is n^7. RHS is Factor * Sigma + (Corrections).
        # Wait, n^7 = n^3 + Factor * Sigma.
        # Implies n^7 - n^3 = Factor * Sigma.
        # Or Factor * Sigma = n^7 - n^3.
        # Sigma = 1/Factor * n^7 - 1/Factor * n^3.
        # So poly = Sigma.
        # If poly has terms other than n^degree, we move them to LHS or keep on RHS?
        
        # Re-reading user request: "sums.txtのpythonが算出した数式を、最大次数の式を左辺にその他の式を右辺に移動させて表示してほしい。"
        # "Display the formula calculated by python in sums.txt with the maximum degree expression on the left side and the other expressions on the right side."
        
        # Example from npower.md:
        # n^6 = n^2 + \frac{6!}{2!3!}\Sigma^{2,3}
        # This means n^6 - n^2 = Factor * Sigma.
        # Sigma = (n^6 - n^2) / Factor = n^6/Factor - n^2/Factor.
        # So if the polynomial from python is n^6/60 - n^2/60.
        # Factor = 720 / (2*6) = 60.
        # Correct.
        
        # So we want to express n^{degree} = (Term from Sigma) + (Correction terms)
        # Actually expanding Factor * Sigma gives n^degree + Factor * rest.
        # So n^degree = Factor * Sigma - Factor * rest.
        
        # Let's compute "Factor * rest".
        # rest = poly - leading_term
        # correction = - Factor * rest
        
        # If correction is positive, we write + term.
        # If correction corresponds to a lower power of n, maybe we can match it to n^k?
        # In npower.md, n^7 = n^3 + ...
        # This implies correction is - (-n^3) = n^3.
        # So Factor * rest was -n^3.
        
        leading_term = leading_coeff * n**degree_val
        rest = poly_expr - leading_term
        
        correction = -1 * factor * rest
        correction_expanded = expand(correction)
        
        # Format the latex
        # n^{degree} = [correction] + \frac{degree!}{p!q!} \Sigma^{p,q}
        
        # Factor string: \frac{N!}{P!Q!}
        # We can construct the boolean correction string
        correction_str = latex(correction_expanded)
        
        # Clean up latex (e.g. 1.0 -> 1)
        correction_str = correction_str.replace('1.0', '1')
        
        # Construct the Sigma term
        sigma_term = f"\\frac{{{degree_val}!}}{{{p}!{q}!}}\\Sigma^{{{p},{q}}}"
        sum_term = f"\\frac{{{degree_val}!}}{{{p}!{q}!}}\\sum_{{k=1}}^{{n-1}} (n-k)^{{{q}}}k^{{{p}}}"
        
        # Combine
        # n^{degree} = correction_str + sigma_term = correction_str + sum_term
        
        if correction_expanded == 0:
            rhs = sigma_term
            rhs_full = sum_term
        else:
            # Handle sign of correction properly in display 
            # latex() usually handles leading minus, but we want "correction + term" or "term + correction"
            # npower.md puts correction first (e.g. n + ...).
            rhs = f"{correction_str} + {sigma_term}"
            rhs_full = f"{correction_str} + {sum_term}"
            
        # Write markdown block
        block = f"$$\nn^{{{degree_val}}} = {rhs} = {rhs_full}\n$$\n\n"
        output.append(block)
        
    print("".join(output))

if __name__ == "__main__":
    process_sums()
