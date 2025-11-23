import matplotlib.pyplot as plt
import tempfile

def save_matplotlib_figure(fig, width=800, height=600):
    """Helper pour sauvegarder une figure matplotlib en PNG."""
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        fig.savefig(tmp.name, dpi=100, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close(fig)  # Libérer la mémoire
        return {"src": tmp.name}
