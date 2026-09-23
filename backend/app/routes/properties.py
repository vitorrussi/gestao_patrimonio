from __future__ import annotations

from flask import Blueprint, jsonify

from app.db import get_session
from app.models import Property
from app.repositories.owned import owned_property, property_payments, user_properties
from app.routes.helpers import current_user_id, no_content, require
from app.schemas.common import api_to_orm, orm_to_api
from app.schemas.properties import PropertyIn
from app.serializers import property_detail_json, property_summary_json
from app.validation import parse_body, parse_patch

properties_bp = Blueprint("properties", __name__, url_prefix="/api/properties")


def _detail(prop: Property):
    return jsonify(property_detail_json(prop, property_payments(get_session(), prop)))


@properties_bp.get("")
def list_properties():
    props = user_properties(get_session(), current_user_id())
    return jsonify([property_summary_json(p) for p in props])


@properties_bp.post("")
def create_property():
    data = parse_body(PropertyIn)
    prop = Property(user_id=current_user_id())
    api_to_orm(data, prop)
    session = get_session()
    session.add(prop)
    session.commit()
    return _detail(prop), 201


@properties_bp.get("/<int:property_id>")
def get_property(property_id: int):
    return _detail(require(owned_property(get_session(), current_user_id(), property_id)))


@properties_bp.patch("/<int:property_id>")
def update_property(property_id: int):
    session = get_session()
    prop = require(owned_property(session, current_user_id(), property_id))
    patch = parse_patch(PropertyIn, orm_to_api(prop, PropertyIn))
    api_to_orm(patch.new, prop)
    session.commit()
    return _detail(prop)


@properties_bp.delete("/<int:property_id>")
def delete_property(property_id: int):
    session = get_session()
    session.delete(require(owned_property(session, current_user_id(), property_id)))
    session.commit()
    return no_content()
