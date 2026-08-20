# Hide and Seek

A Python-based application that models a zero-sum "Hide and Seek" game scenario, utilizing a graphical user interface and an underlying linear programming solver to evaluate optimal strategies and payoffs.

## Project Structure

The codebase is organized into modular components separating the mathematical engine, game state, and user interface:

*   **`src/core/`**: Core contracts and base interface definitions.
*   **`src/engine/`**: The mathematical and logical backbone for solving the zero-sum game.
    *   `lp_solver.py`: Handles linear programming computations and matrix operations to find optimal mixed strategies.
    *   `payoff.py`: Calculates outcomes and strategy evaluations for the zero-sum payoff matrices.
    *   `world.py` & `models.py`: Defines the environment and core data structures.
*   **`src/game/`**: Contains `game_controller.py` to manage the interaction between the engine and the UI.
*   **`src/ui/`**: The graphical interface implementation (utilizing Qt/QSS).
    *   `main.py`: The UI entry point.
    *   `screens/` & `components/`: Modular views including start and game screens, and confirmation dialogs.
    *   `styles/theme.qss`: Application styling and visual themes.
*   **`tests/`**: Unit testing directories to verify engine logic and solver accuracy.

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/3li-3mr/hide_n_seek.git](https://github.com/3li-3mr/hide_n_seek.git)
    cd hide_n_seek
    ```

2.  **Install dependencies:**
    Ensure you have an active Python environment. Install the required packages listed in the requirements file:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application:**
    Launch the application via the main UI script:
    ```bash
    python src/ui/main.py
    ```

## Development

*   **UI Modifications:** Adjust the application's appearance by modifying the stylesheet at `src/ui/styles/theme.qss`. Custom fonts like `OrbitronBlack` are located in `src/ui/assets/`.
*   **Engine Logic:** When updating the `lp_solver.py` or `payoff.py` for the zero-sum evaluation logic, ensure that changes to the simplex logic or payoff matrices are covered by tests in `src/engine/tests.py` or the root `tests/` directory.
