from datetime import datetime
from dateutil.relativedelta import relativedelta

from feast import FeatureStore, repo_config, Entity, FeatureView, FeatureService
from feast.data_source import DataSource

from feast.infra.offline_stores.dask import (
    DaskOfflineStoreConfig,
)

from feature_repo import entities, feature_views

store =  None
def get_store():
    global store
    if store is None:        store = FeatureStore(repo_path=".")
    return store

def apply_store(store: FeatureStore):
    list_entities = [
        getattr(entities, o)
        for o in dir(entities)
        if isinstance(getattr(entities, o), Entity)
    ]
    list_feature_views = [
        getattr(feature_views, o)
        for o in dir(feature_views)
        if isinstance(getattr(feature_views, o), FeatureView)
    ]

    list_datasources = [
        getattr(feature_views, o)
        for o in dir(feature_views)
        if isinstance(getattr(feature_views, o), DataSource)
    ]

    list_entities_name = list(map(lambda x: x.name, list_entities))
    list_feature_views_name = list(map(lambda x: x.name, list_feature_views))

    list_datasources_name = list(map(lambda x: x.name, list_datasources))

    previous_entities = store.list_entities()
    previous_feature_views = store.list_feature_views()

    preivous_datasources = store.list_data_sources()

    entities_to_delete = [
        entity for entity in previous_entities if entity.name not in list_entities_name
    ]
    feature_views_delete = [
        fv for fv in previous_feature_views if fv.name not in list_feature_views_name
    ]

    datasources_delete = [
        ds for ds in preivous_datasources if ds.name not in list_datasources_name
    ]

    store.apply(
        objects=[
            *list_entities,
            *list_datasources,
 
            *list_feature_views,
        ],
        objects_to_delete=[
            *entities_to_delete,
            *datasources_delete,
            *feature_views_delete,

        ],
        partial=False,
    )


if __name__ == "__main__":
    store = get_store()
    apply_store(store=store)
    dt = datetime.now()
    store.materialize(start_date=dt - relativedelta(months=24), end_date=dt)
