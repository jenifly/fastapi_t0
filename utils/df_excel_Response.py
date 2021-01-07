from typing import Any
from io import BytesIO
from urllib.parse import quote

import pandas as pd

from starlette.responses import Response

class DataFrameResponse(Response):
    def __init__(
        self,
        dataframe: Any,
        filename: str,
        index: bool = False
    ) -> None:
        self.status_code = 200
        self.media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        outfile = BytesIO()
        dataframe.to_excel(outfile, index=index)
        self.body = outfile.getvalue()
        outfile.close()
        self.init_headers({"Content-Disposition": f"attachment;fileName={quote(filename)}"})
        self.background = None
