from playwright.sync_api import expect

from eventos_app.test.test_e2e.base import BaseE2ETest


# Tests para la página de inicio
class HomePageDisplayTest(BaseE2ETest):
    """Tests relacionados con la visualización de la página de inicio"""

    def test_home_page_loads(self):
        """Test que verifica que la home carga correctamente"""
        self.page.goto(f"{self.live_server_url}/")

        # Verificar que el logo este presente
        logo = self.page.get_by_role("link", name="Eventos").first
        expect(logo).to_be_visible()
        expect(logo).to_have_attribute("href", "/")

        # Verificar textos principales de la página
        expect(self.page.get_by_text("Eventos y Entradas")).to_be_visible()
        expect(
            self.page.get_by_text(
                "Descubre, organiza y participa en los mejores eventos. Compra entradas, deja comentarios y califica tus experiencias."
            )
        ).to_be_visible()
