from flask import Blueprint, current_app, jsonify, request, send_file

from .catalog import document_path, find_institution, list_institutions
from .pdf_service import DocumentReadError, search_pages


api = Blueprint("api", __name__)


@api.get("/health")
def health():
    institutions = list_institutions(current_app.config["DATASET_DIR"])
    return jsonify({"status": "ok", "dataset_count": len(institutions)})


@api.get("/institutions")
def institutions():
    items = list_institutions(current_app.config["DATASET_DIR"])
    return jsonify({"count": len(items), "institutions": items})


@api.get("/institutions/<institution_id>")
def institution(institution_id):
    item = find_institution(current_app.config["DATASET_DIR"], institution_id)
    if item is None:
        return jsonify({"error": "Institution not found."}), 404
    return jsonify(item)


@api.get("/institutions/<institution_id>/document")
def institution_document(institution_id):
    item = find_institution(current_app.config["DATASET_DIR"], institution_id)
    if item is None:
        return jsonify({"error": "Institution not found."}), 404
    return send_file(
        document_path(current_app.config["DATASET_DIR"], item),
        mimetype="application/pdf",
        as_attachment=False,
        download_name=item["filename"],
    )


@api.get("/search")
def search():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "A non-empty 'q' search parameter is required."}), 400
    if len(query) > 200:
        return jsonify({"error": "Search query must be 200 characters or fewer."}), 400

    try:
        limit = int(request.args.get("limit", "20"))
    except ValueError:
        return jsonify({"error": "'limit' must be an integer from 1 to 100."}), 400
    if not 1 <= limit <= 100:
        return jsonify({"error": "'limit' must be an integer from 1 to 100."}), 400

    dataset_dir = current_app.config["DATASET_DIR"]
    institution_id = request.args.get("institution_id")
    if institution_id is not None:
        selected = find_institution(dataset_dir, institution_id)
        if selected is None:
            return jsonify({"error": "Institution not found."}), 404
        items = [selected]
    else:
        items = list_institutions(dataset_dir)

    results = []
    try:
        for item in items:
            pages = search_pages(document_path(dataset_dir, item), query, limit)
            for page in pages:
                results.append(
                    {
                        "institution_id": item["id"],
                        "institution": item["name"],
                        **page,
                    }
                )
                if len(results) >= limit:
                    break
            if len(results) >= limit:
                break
    except DocumentReadError as error:
        current_app.logger.exception("Dataset PDF search failed")
        return jsonify({"error": str(error)}), 500

    return jsonify({"query": query, "count": len(results), "results": results})
