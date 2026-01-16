#!/usr/bin/env python3
"""
AgentNote Web UI
Markdown Blog Viewer
"""

import sys
import os
import signal
import subprocess
import time
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))


def kill_port(port):
    """Kill process using the specified port"""
    try:
        # Find process using the port
        result = subprocess.run(
            ['lsof', '-ti', f':{port}'],
            capture_output=True, text=True
        )
        pids = result.stdout.strip().split('\n')

        for pid in pids:
            if pid:
                try:
                    os.kill(int(pid), signal.SIGKILL)
                    print(f"Killed process {pid} on port {port}")
                except ProcessLookupError:
                    pass

        # Wait for port to be released
        for _ in range(10):  # Wait up to 5 seconds
            result = subprocess.run(
                ['lsof', '-ti', f':{port}'],
                capture_output=True, text=True
            )
            if not result.stdout.strip():
                return  # Port is free
            time.sleep(0.5)
        print(f"Warning: Port {port} might still be in use.")
    except Exception:
        pass  # No process on port or lsof not available

from flask import Flask, render_template, request, jsonify
from db import (
    init_database, DB_PATH,
    add_document, get_document, update_document, delete_document,
    search_documents, get_recent_documents, get_categories, get_all_tags,
    get_documents_count
)

app = Flask(__name__)


# === Page Routes ===

@app.route('/')
def index():
    """Main page - Blog view"""
    return render_template('index.html')


# === API Routes ===

@app.route('/api/docs', methods=['GET'])
def api_get_docs():
    """Get documents list"""
    keyword = request.args.get('keyword', '')
    category = request.args.get('category', '')
    tag = request.args.get('tag', '')
    limit = request.args.get('limit', 20, type=int)
    offset = request.args.get('offset', 0, type=int)

    docs = search_documents(
        keyword=keyword if keyword else None,
        category=category if category else None,
        tag=tag if tag else None,
        limit=limit,
        offset=offset
    )
    total = get_documents_count()

    return jsonify({
        'success': True,
        'data': docs,
        'total': total
    })


@app.route('/api/docs/<int:doc_id>', methods=['GET'])
def api_get_doc_by_id(doc_id):
    """Get document by ID"""
    doc = get_document(doc_id=doc_id)
    if doc:
        return jsonify({'success': True, 'data': doc})
    return jsonify({'success': False, 'error': 'Document not found'}), 404


@app.route('/api/docs/slug/<slug>', methods=['GET'])
def api_get_doc_by_slug(slug):
    """Get document by slug"""
    doc = get_document(slug=slug)
    if doc:
        return jsonify({'success': True, 'data': doc})
    return jsonify({'success': False, 'error': 'Document not found'}), 404


@app.route('/api/docs', methods=['POST'])
def api_add_doc():
    """Add new document"""
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400

    if not data.get('title') or not data.get('content'):
        return jsonify({'success': False, 'error': 'title and content are required'}), 400

    try:
        result = add_document(
            title=data['title'],
            content=data['content'],
            category=data.get('category'),
            tags=data.get('tags', []),
            summary=data.get('summary'),
            source=data.get('source', 'web')
        )
        return jsonify({
            'success': True,
            'id': result['id'],
            'slug': result['slug'],
            'message': f'Document saved: {result["title"]}'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/docs/<int:doc_id>', methods=['PUT'])
def api_update_doc(doc_id):
    """Update document"""
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400

    try:
        success = update_document(doc_id, **data)
        if success:
            return jsonify({'success': True, 'message': 'Document updated'})
        return jsonify({'success': False, 'error': 'Document not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/docs/<int:doc_id>', methods=['DELETE'])
def api_delete_doc(doc_id):
    """Delete document"""
    try:
        success = delete_document(doc_id)
        if success:
            return jsonify({'success': True, 'message': 'Document deleted'})
        return jsonify({'success': False, 'error': 'Document not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/categories', methods=['GET'])
def api_get_categories():
    """Get all categories"""
    categories = get_categories()
    return jsonify({'success': True, 'data': categories})


@app.route('/api/tags', methods=['GET'])
def api_get_tags():
    """Get all tags"""
    tags = get_all_tags()
    return jsonify({'success': True, 'data': tags})


@app.route('/api/recent', methods=['GET'])
def api_get_recent():
    """Get recent documents"""
    limit = request.args.get('limit', 10, type=int)
    docs = get_recent_documents(limit=limit)
    return jsonify({'success': True, 'data': docs})


@app.route('/api/stats', methods=['GET'])
def api_get_stats():
    """Get statistics"""
    return jsonify({
        'success': True,
        'data': {
            'total_docs': get_documents_count(),
            'categories': get_categories(),
            'tags': get_all_tags()
        }
    })


# === Error Handlers ===

@app.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500


# === Main ===

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    parser.add_argument('--port', type=int, default=5000, help='Port number')
    args = parser.parse_args()

    # Kill any existing process on the port
    kill_port(args.port)

    # Ensure database exists
    if not DB_PATH.exists():
        init_database()

    print("Starting AgentNote Blog Viewer...")
    print(f"Open http://localhost:{args.port} in your browser")
    app.run(host='0.0.0.0', port=args.port, debug=args.debug, use_reloader=False)
