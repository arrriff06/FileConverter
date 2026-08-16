from flask import Blueprint, render_template, request, jsonify
import random
import string
import time

room_bp = Blueprint("room", __name__)

# Temporary in-memory room storage
rooms = {}

ROOM_EXPIRY = 60 * 60  # 1 hour


def generate_room_code():
    """Generate a unique 6-character room code."""

    while True:
        code = ''.join(
            random.choices(
                string.ascii_uppercase + string.digits,
                k=6
            )
        )

        if code not in rooms:
            return code


def cleanup_rooms():
    """Remove rooms older than the expiry time."""

    current_time = time.time()

    expired_rooms = [
        code
        for code, room in rooms.items()
        if current_time - room["created_at"] > ROOM_EXPIRY
    ]

    for code in expired_rooms:
        del rooms[code]


# --------------------------------------------------
# ROOM PAGE
# --------------------------------------------------

@room_bp.route("/room")
def room_page():
    return render_template("room.html")


# --------------------------------------------------
# CREATE ROOM
# --------------------------------------------------

@room_bp.route("/room/create", methods=["POST"])
def create_room():

    cleanup_rooms()

    code = generate_room_code()

    rooms[code] = {
        "content": "",
        "type": "text",
        "created_at": time.time()
    }

    return jsonify({
        "success": True,
        "code": code
    })


# --------------------------------------------------
# GET ROOM
# --------------------------------------------------

@room_bp.route("/room/<code>", methods=["GET"])
def get_room(code):

    cleanup_rooms()

    code = code.upper().strip()

    room = rooms.get(code)

    if not room:
        return jsonify({
            "success": False,
            "error": "Room not found or expired."
        }), 404

    return jsonify({
        "success": True,
        "code": code,
        "content": room["content"],
        "type": room["type"]
    })


# --------------------------------------------------
# UPDATE ROOM
# --------------------------------------------------

@room_bp.route("/room/<code>/update", methods=["POST"])
def update_room(code):

    cleanup_rooms()

    code = code.upper().strip()

    room = rooms.get(code)

    if not room:
        return jsonify({
            "success": False,
            "error": "Room not found or expired."
        }), 404

    data = request.get_json(silent=True) or {}

    content = data.get("content", "")
    content_type = data.get("type", "text")

    room["content"] = content
    room["type"] = content_type

    return jsonify({
        "success": True
    })


# --------------------------------------------------
# DELETE ROOM
# --------------------------------------------------

@room_bp.route("/room/<code>", methods=["DELETE"])
def delete_room(code):

    code = code.upper().strip()

    if code in rooms:
        del rooms[code]

    return jsonify({
        "success": True
    })