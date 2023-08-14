import datetime as dt
from typing import Optional

import config
from fastapi import Depends, FastAPI, Request
from pydantic import BaseModel
from models import get_db, Metric as MetricModel
from sqlalchemy.orm import Session

from value_logger.utils import get_secret_key


def gsk(request: Request):
    return get_secret_key(request=request, secret_key=config.SECRET_KEY)


app = FastAPI(dependencies=[Depends(get_secret_key)])


class Metric(BaseModel):
    device_name: str
    metric_name: str
    metric_value: float
    timestamp: dt.datetime


class Metrics(BaseModel):
    metrics: list[Metric]


class PostResponse(BaseModel):
    added_metrics: int


@app.post("/metrics/")
async def create_metrics(
    metrics_in: Metrics,
    db: Session = Depends(get_db),
):
    metrics = [MetricModel(**metric.model_dump()) for metric in metrics_in.metrics]

    db.add_all(metrics)
    db.commit()
    db.flush(metrics)

    return PostResponse(added_metrics=len(metrics))


class MetricQuery(BaseModel):
    device_name: Optional[str] = None
    metric_name: Optional[str] = None
    start_time: Optional[dt.datetime] = None
    end_time: Optional[dt.datetime] = None


@app.get("/metrics/")
async def get_metrics(
    query: MetricQuery = Depends(), db: Session = Depends(get_db)
) -> Metrics:
    metrics_query = db.query(MetricModel)

    if query.device_name:
        metrics_query = metrics_query.filter(
            MetricModel.device_name == query.device_name
        )

    if query.metric_name:
        metrics_query = metrics_query.filter(
            MetricModel.metric_name == query.metric_name
        )

    if query.start_time:
        metrics_query = metrics_query.filter(MetricModel.timestamp >= query.start_time)

    if query.end_time:
        metrics_query = metrics_query.filter(MetricModel.timestamp <= query.end_time)

    metrics = metrics_query.all()
    return Metrics(metrics=[Metric(**metric.__dict__) for metric in metrics])
