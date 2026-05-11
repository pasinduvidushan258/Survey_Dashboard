from nicegui import ui
import pandas as pd
import sqlite3
import temp_db

def show_review_window(cleaned_df_initial, removed_df_initial, survey_name, year, metadata=None):
    """
    Display a review dialog for cleaned and removed survey data.

    This interface allows users to:
    - Review removed rows (duplicates and low-completion rows)
    - Restore individual removed rows back into the cleaned dataset
    - Download the cleaned dataset as a CSV file
    - Save the cleaned dataset into a SQLite database

    Parameters:
    ----------
    cleaned_df_initial : pandas.DataFrame
        The cleaned dataset after preprocessing.

    removed_df_initial : pandas.DataFrame
        The dataset containing rows removed during cleaning.

    survey_name : str
        Name of the survey.

    year : str or int
        Year of the survey.

    metadata : dict, optional
        Additional information about the cleaning process, including:
        - removed_empty_count
        - removed_duplicates_count
        - removed_columns
        - combined_columns
    """

    # Ensure metadata is always a dictionary
    metadata = metadata or {}

    # Maintain local application state for dynamic updates
    state = {
        'cleaned': cleaned_df_initial.copy(),
        'removed': removed_df_initial.copy()
    }

    # Create dialog UI container
    with ui.dialog() as dialog, ui.card().classes('w-11/12 max-w-7xl h-[85vh] flex flex-col p-6'):

        # =========================
        # 1. Dialog Title
        # =========================
        ui.label(f'Data Cleaning Review : {survey_name} ({year})') \
            .classes('text-2xl font-bold text-[#0b1132] mb-4')

        # =========================
        # 2. Action Buttons (Download, Save, Cancel)
        # =========================
        with ui.row().classes('w-full justify-between items-center mb-4 p-3 bg-gray-50 rounded shadow-sm'):

            with ui.row().classes('gap-4'):

                # Download cleaned dataset as CSV
                ui.button(
                    'Download Cleaned CSV',
                    icon='download',
                    on_click=lambda: ui.download(
                        state['cleaned'].to_csv(index=False).encode(),
                        f'{survey_name}_Cleaned.csv'
                    )
                ).classes('bg-blue-500 hover:bg-blue-600 text-white')

                # Save cleaned dataset to SQLite database
                ui.button(
                    'Confirm & Save to Database',
                    icon='storage',
                    on_click=lambda: save_to_db()
                ).classes('bg-green-600 hover:bg-green-700 text-white')

            # Close dialog without saving
            ui.button('Cancel', icon='close', on_click=dialog.close).props('flat color=red')

        # =========================
        # 3. Data Review Section
        # =========================
        with ui.column().classes('w-full flex-grow overflow-auto gap-4'):
            removed_container = ui.column().classes(
                'w-full overflow-auto border rounded p-3 bg-white max-h-[70vh]'
            )

        # Split removed data into categories based on reason
        if 'reason' in state['removed'].columns:
            reason_series = state['removed']['reason'].astype(str)
            duplicate_removed = state['removed'][reason_series == 'Duplicate row']
            empty_removed = state['removed'][reason_series.str.contains('Filled <', na=False)]
        else:
            duplicate_removed = state['removed'].iloc[0:0]
            empty_removed = state['removed'].iloc[0:0]

        # Extract metadata or fallback to calculated values
        removed_empty_count = metadata.get('removed_empty_count', len(empty_removed))
        removed_duplicate_count = metadata.get('removed_duplicates_count', len(duplicate_removed))
        removed_columns = metadata.get('removed_columns', [])
        combined_columns = metadata.get('combined_columns', [])

        # =========================
        # 4. Summary Cards
        # =========================
        with ui.row().classes('w-full gap-4 mb-4'):

            # Row removal summary
            with ui.card().classes('w-full p-4 border border-gray-200'):
                ui.label('Row Removal Summary').classes('text-lg font-semibold')
                ui.label(f'Duplicate rows removed: {removed_duplicate_count}').classes('text-sm')
                ui.label(f'Empty-percentage rows removed: {removed_empty_count}').classes('text-sm')

            # Column transformation summary
            with ui.card().classes('w-full p-4 border border-gray-200'):
                ui.label('Column Removal Summary').classes('text-lg font-semibold')
                ui.label(f'Explicitly dropped columns: {len(removed_columns)}').classes('text-sm')
                ui.label(f'Combined duplicate columns: {len(combined_columns)}').classes('text-sm')

                if removed_columns:
                    ui.label(f'Removed columns: {", ".join(removed_columns)}') \
                        .classes('text-xs text-gray-700')

                if combined_columns:
                    ui.label(f'Combined columns: {", ".join(combined_columns)}') \
                        .classes('text-xs text-gray-700')

        # =========================
        # 5. Render Removed Data Tables
        # =========================
        def render_removed_table():
            """Render removed data grouped by reason."""
            removed_container.clear()

            with removed_container:

                # Duplicate rows section
                ui.label('REMOVED DATA – DUPLICATE ROWS') \
                    .classes('text-lg font-semibold text-red-600 mb-2')

                if not duplicate_removed.empty:
                    render_removal_subset(duplicate_removed)
                else:
                    ui.label('No duplicate rows removed.').classes('p-2 text-green-600')

                # Low completion rows section
                ui.label('REMOVED DATA – EMPTY PERCENTAGE ROWS') \
                    .classes('text-lg font-semibold text-red-600 mt-4 mb-2')

                if not empty_removed.empty:
                    render_removal_subset(empty_removed)
                else:
                    ui.label('No low-completion rows removed.').classes('p-2 text-green-600')

        def render_removal_subset(subset_df):
            """
            Render a table for a subset of removed data with a restore action.
            """
            rows = subset_df.to_dict('records')

            columns = [
                {'name': str(col), 'label': str(col).upper(), 'field': str(col), 'align': 'left'}
                for col in subset_df.columns
            ]

            # Add action column for restoring rows
            columns.append({
                'name': 'action',
                'label': 'RESTORE',
                'field': 'action',
                'align': 'center'
            })

            table = ui.table(
                columns=columns,
                rows=rows,
                row_key='row_id'
            ).classes('w-full').props('dense bordered sticky-header')

            # Custom button for restoring a row
            table.add_slot('body-cell-action', '''
                <q-td :props="props">
                    <q-btn flat icon="undo" color="negative" dense
                        @click="() => $parent.$emit('restore', props.row)">
                        <q-tooltip>Restore this row</q-tooltip>
                    </q-btn>
                </q-td>
            ''')

            table.on('restore', handle_restore)

        def handle_restore(e):
            """
            Restore a removed row back into the cleaned dataset.
            """
            row_data = e.args
            r_id = row_data.get('row_id')

            if r_id is None:
                return

            # Retrieve the row to restore
            row_to_restore = state['removed'][state['removed']['row_id'] == r_id].copy()

            # Remove 'reason' column before restoring
            if 'reason' in row_to_restore.columns:
                row_to_restore = row_to_restore.drop(columns=['reason'])

            # Append row back to cleaned dataset
            state['cleaned'] = pd.concat([state['cleaned'], row_to_restore], ignore_index=True)

            # Remove restored row from removed dataset
            state['removed'] = state['removed'][state['removed']['row_id'] != r_id]

            # Recalculate subsets
            nonlocal duplicate_removed, empty_removed
            if 'reason' in state['removed'].columns:
                reason_series = state['removed']['reason'].astype(str)
                duplicate_removed = state['removed'][reason_series == 'Duplicate row']
                empty_removed = state['removed'][reason_series.str.contains('Filled <', na=False)]
            else:
                duplicate_removed = state['removed'].iloc[0:0]
                empty_removed = state['removed'].iloc[0:0]

            # Refresh UI
            render_removed_table()

            ui.notify(f'Row {r_id} restored!', color='warning', position='top')

        # Initial render
        render_removed_table()

        # =========================
        # 6. Save to Database
        # =========================
        def save_to_db():
            """
            Save the cleaned dataset into a SQLite database table.
            """
            try:
                table_name = f"{survey_name.replace(' ', '_').lower()}_{year}"
                final_df = state['cleaned'].copy()

                # Remove internal tracking column if present
                if 'row_id' in final_df.columns:
                    final_df = final_df.drop(columns=['row_id'])

                # Write data to SQLite database
                conn = sqlite3.connect('survey.db')
                final_df.to_sql(table_name, conn, if_exists='replace', index=False)
                conn.close()

                ui.notify(f'Data saved to table: {table_name} 💾',
                          color='positive', position='top')

                # Cleanup temporary staging database
                temp_db.drop_staging_db()

                # Close dialog and navigate to home
                dialog.close()
                ui.navigate.to('/home')

            except Exception as e:
                ui.notify(f'Database Error: {e}',
                          color='negative', position='top')

    # Open the dialog window
    dialog.open()