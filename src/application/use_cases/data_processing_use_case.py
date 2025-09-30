# src/application/use_cases/data_processing_use_case.py
from camelot.io import read_pdf
from pandas import DataFrame, Series, concat, isna, read_csv, to_datetime, to_numeric

from domain.entities.document import DataProcessingConfig
from domain.repositories.data_repository import DataRepository


class DataProcessingUseCase:
    """Caso de uso para processamento de dados SRAG."""

    def __init__(self, data_repository: DataRepository) -> None:
        """
        Inicializa caso de uso de processamento.

        Args:
            data_repository: Repositório de dados
        """
        self.data_repository = data_repository

    def process_pdf_dictionary(self, pdf_path: str) -> DataFrame:
        """
        Processa dicionário de dados do PDF.

        Args:
            pdf_path: Caminho para o arquivo PDF

        Returns:
            DataFrame com dicionário processado
        """
        for df in (
            dfs := [
                table.df for table in read_pdf(pdf_path, pages="all", line_scale=40)
            ][1:]
        ):
            df.columns = dfs[0].iloc[0]

        dfs[0].drop(index=0, inplace=True)
        final_df = concat(self._merge_split_rows(dfs), ignore_index=True)
        final_df["Tipo"] = final_df["Tipo"].str.replace("\n", "")

        return final_df

    def download_and_process_srag_data(
        self, years: list[int], config: DataProcessingConfig
    ) -> DataFrame:
        """
        Baixa e processa dados SRAG.

        Args:
            years: Lista de anos para processar
            config: Configuração de processamento

        Returns:
            DataFrame consolidado
        """
        dfs = []
        for year in years:
            print(f"Baixando dados do ano {year}...")
            dfs.append(
                self._apply_dtype_conversions(
                    read_csv(
                        f"https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SRAG/{year}/INFLUD{year}-26-06-2025.csv",
                        sep=config.separator,
                        encoding=config.encoding,
                        low_memory=False,
                    ),
                    config,
                )
            )
        return concat(dfs, ignore_index=True)

    def _apply_dtype_conversions(
        self, df: DataFrame, config: DataProcessingConfig
    ) -> DataFrame:
        """Aplica conversões de tipo aos dados."""
        df_converted = df.copy()

        # Aplicar conversões baseadas em padrões
        for col in df_converted.columns:
            col_type = str(df_converted[col].dtype)

            if col_type == "object":
                # Tentar converter datas
                if any(keyword in col.upper() for keyword in ["DT_", "DATA"]):
                    df_converted[col] = to_datetime(
                        df_converted[col], format=config.date_format, errors="coerce"
                    )
                # Tentar converter números
                elif df_converted[col].str.match(r"^\d+$", na=False).any():
                    df_converted[col] = to_numeric(df_converted[col], errors="coerce")

        return df_converted

    def _merge_split_rows(self, dfs: list[DataFrame]) -> list[DataFrame]:
        """Mescla linhas divididas entre páginas do PDF."""
        if not dfs:
            return []

        processed_dfs: list[DataFrame] = []

        for i, df in enumerate(dfs):
            processed_df = self._process_single_dataframe(
                df, processed_dfs[-1] if processed_dfs else None
            )
            if len(processed_df) > 0:
                processed_dfs.append(processed_df)

        return processed_dfs

    def _process_single_dataframe(
        self, df: DataFrame, previous_df: DataFrame | None
    ) -> DataFrame:
        """Processa DataFrame individual verificando continuações."""
        if len(df) == 0:
            return df.copy()

        current_df = df.copy()
        first_row = current_df.iloc[0]

        if self._is_continuation_row(first_row) and previous_df is not None:
            self._merge_continuation_row(previous_df, first_row)
            current_df = current_df.iloc[1:].copy()

        return DataFrame(current_df)

    def _is_continuation_row(self, row: Series) -> bool:
        """Verifica se a linha é continuação da página anterior."""
        if len(row) < 5:
            return False

        return all(
            isna(row.iloc[j]) or str(row.iloc[j]).strip() == "" for j in range(3)
        ) and any(
            not isna(row.iloc[j]) and str(row.iloc[j]).strip() != ""
            for j in range(2, 5)
        )

    def _merge_continuation_row(
        self, target_df: DataFrame, continuation_row: Series
    ) -> None:
        """Mescla linha de continuação com DataFrame alvo."""
        if len(target_df) == 0:
            return

        last_row_idx = target_df.index[-1]
        for col_idx in range(len(continuation_row)):
            if col_idx >= len(target_df.columns):
                break

            col_name = target_df.columns[col_idx]
            continuation_value = continuation_row.iloc[col_idx]

            if isna(continuation_value) or str(continuation_value).strip() == "":
                continue

            existing_value = target_df.loc[last_row_idx, col_name]

            if isna(existing_value) or str(existing_value).strip() == "":
                target_df.loc[last_row_idx, col_name] = continuation_value
            else:
                existing = str(existing_value).strip()
                new_content = str(continuation_value).strip()
                target_df.loc[last_row_idx, col_name] = f"{existing} {new_content}"
