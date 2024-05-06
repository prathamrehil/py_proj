import pyperclip

# List of physics formulas with LaTeX formatting
physics_formulas = [
    "1. Displacement (\\( \\Delta x \\)) = \\( x_f - x_i \\)",
    "2. Average velocity (\\( \\overline{v} \\)) = \\( \\frac{\\Delta x}{\\Delta t} \\)",
    "3. Average acceleration (\\( \\overline{a} \\)) = \\( \\frac{\\Delta v}{\\Delta t} \\)",
    "4. Newton's second law: \\( F = ma \\)",
    "5. Weight (\\( W \\)) = \\( mg \\)",
    "6. Frictional force (\\( f \\)) = \\( \\mu N \\)",
    "7. Work (\\( W \\)) = \\( F \\cdot d \\cdot \\cos(\\theta) \\)",
    "8. Kinetic energy (\\( KE \\)) = \\( \\frac{1}{2}mv^2 \\)",
    "9. Potential energy (\\( PE \\)) = \\( mgh \\)",
    "10. Power (\\( P \\)) = \\( \\frac{W}{t} \\)",
    "11. Impulse (\\( J \\)) = \\( F \\cdot \\Delta t \\)",
    "12. Momentum (\\( p \\)) = \\( mv \\)",
    "13. Law of conservation of momentum: \\( \\sum p_{\\text{initial}} = \\sum p_{\\text{final}} \\)",
    "14. Gravitational force (\\( F_g \\)) = \\( G \\frac{m_1 m_2}{r^2} \\)",
    "15. Elastic potential energy (\\( U_e \\)) = \\( \\frac{1}{2} k x^2 \\)",
    "16. Hooke's Law: \\( F = kx \\)",
    "17. Torque (\\( \\tau \\)) = \\( r \\times F \\times \\sin(\\theta) \\)",
    "18. Moment of inertia (\\( I \\)) = \\( \\sum m_i r_i^2 \\)",
    "19. Angular momentum (\\( L \\)) = \\( I\\omega \\)",
    "20. Law of conservation of"
]

# Join the formulas with newlines
formatted_text = '\n'.join(physics_formulas)

# Copy the formatted text to the clipboard
pyperclip.copy(formatted_text)

print("Formatted physics formulas copied to clipboard.")
