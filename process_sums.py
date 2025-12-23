import re
from sympy import Symbol, expand, summation, sympify, Add, degree, Poly

def process_file():
    path = r'c:\sheare\masatoyo\RONET\HP\testpages\sums.txt'
    content = ""
    try:
        with open(path, 'r', encoding='utf-16') as f:
            content = f.read()
    except Exception:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            return

    lines = content.splitlines()
    
    n = Symbol('n')
    current_expr = None
    
    results = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if line is an input expression
        if 'expand(summation' in line:
            # Clean up >>> prompt
            clean_line = line.replace('>>>', '').strip()
            current_expr = clean_line
            continue
            
        # If we have an expression, this line should be the result
        if current_expr:
            try:
                # Parse the polynomial
                poly_expr = sympify(line)
                
                # Find max degree term
                # We assume polynomial in n
                if not poly_expr.has(n):
                    current_expr = None
                    continue
                    
                p = Poly(poly_expr, n)
                deg = p.degree()
                max_term = p.coeff_monomial(n**deg) * n**deg
                
                rest = poly_expr - max_term
                # rest needs to be subtracted from the LHSside (which is the summation)
                # Equation: MaxTerm = Summation - Rest
                # So we display: MaxTerm = Summation - (Rest)
                
                # Format:
                # n^7/140 = expand(summation(...)) - (n^3/60 - n/42)
                
                # But we want to negate Rest to put it on the other side
                # Original: Summation = MaxTerm + Rest
                # Rearranged: MaxTerm = Summation - Rest
                
                neg_rest = -rest
                # We want to format it nicely
                
                print(f"{max_term} = {current_expr} + ({neg_rest})")
                
                current_expr = None
            except Exception as e:
                # Not a valid poly or parse error, skip
                # print(f"Skipping line: {line} due to {e}")
                pass

if __name__ == '__main__':
    process_file()
