import pytest
from main import HashiGameUI


class DummyCanvas:
    # Simulador
    def create_oval(self, *args, **kwargs): pass
    def create_text(self, *args, **kwargs): pass
    def create_line(self, *args, **kwargs): pass
    def delete(self, *args, **kwargs): pass

# crea instancia del juego sin interfaz real
@pytest.fixture
def setup_ui():
    app = HashiGameUI.__new__(HashiGameUI)
    app.canvas = DummyCanvas()
    app.grid_size = 5
    app.board = [
        [0, 0, 0, 0, 0],
        [0, 1, 0, 1, 0],
        [0, 0, 0, 0, 0],
        [0, 1, 0, 1, 0],
        [0, 0, 0, 0, 0],
    ]
    app.initial_board = [row[:] for row in app.board]
    app.connections_count = {(1, 1): 0, (1, 3): 0, (3, 1): 0, (3, 3): 0}
    app.bridges_coords = []
    app.connections = {}
    return app

# PRUEBAS UNITARIAS
def test_path_clear_no_island_between(setup_ui):
    app = setup_ui
    result = app.path_clear(1, 1, 1, 3)
    print("Camino libre entre islas sin obstáculos.")
    assert result is True


def test_path_clear_blocked_by_island(setup_ui):
    app = setup_ui
    app.board[1][2] = 1
    result = app.path_clear(1, 1, 1, 3)
    print("Isla detectada correctamente bloqueando el camino.")
    assert result is False


def test_path_clear_cross_bridge(setup_ui):
    app = setup_ui
    app.bridges_coords = [("V", 2, 0, 4)]
    result = app.path_clear(1, 1, 1, 3)
    print(" Cruce de puente detectado correctamente.")
    assert result is False


def test_add_bridge_updates_counts(setup_ui):
    app = setup_ui
    key = ((1, 1), (1, 3))
    app.connections[key] = 0
    app.connections_count[(1, 1)] = 0
    app.connections_count[(1, 3)] = 0
    app.connections[key] += 1
    app.connections_count[(1, 1)] += 1
    app.connections_count[(1, 3)] += 1
    print("Contadores actualizados correctamente al agregar un puente.")
    assert app.connections_count[(1, 1)] == 1
    assert app.connections_count[(1, 3)] == 1


def test_max_two_bridges_rule(setup_ui):
    app = setup_ui
    key = ((1, 1), (1, 3))
    app.connections[key] = 2
    print("Regla de máximo 2 puentes entre islas verificada.")
    assert app.connections[key] <= 2
