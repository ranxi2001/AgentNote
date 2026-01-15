#!/usr/bin/env python3
"""
AgentNote Web UI
Flask application for the AgentNote knowledge base
"""

import sys
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))

from flask import Flask, render_template, request, jsonify
from db import (
    init_database, DB_PATH,
    add_idea, get_idea, update_idea, delete_idea,
    search_ideas, get_recent_ideas, get_categories,
    add_relation, get_relations
)

app = Flask(__name__)


# === Page Routes ===

@app.route('/')
def index():
    """Main page - Chat-first interface"""
    return render_template('index.html')


# === API Routes ===

@app.route('/api/ideas', methods=['GET'])
def api_get_ideas():
    """Get ideas list with optional filtering"""
    keyword = request.args.get('keyword', '')
    category = request.args.get('category', '')
    limit = request.args.get('limit', 20, type=int)
    offset = request.args.get('offset', 0, type=int)

    ideas = search_ideas(
        keyword=keyword if keyword else None,
        category=category if category else None,
        limit=limit,
        offset=offset
    )
    return jsonify({'success': True, 'data': ideas})


@app.route('/api/ideas', methods=['POST'])
def api_add_idea():
    """Add a new idea"""
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400

    if not data.get('title') or not data.get('content'):
        return jsonify({'success': False, 'error': 'title and content are required'}), 400

    try:
        idea_id = add_idea(
            title=data['title'],
            content=data['content'],
            category=data.get('category'),
            keywords=data.get('keywords', []),
            source=data.get('source', 'web')
        )
        return jsonify({
            'success': True,
            'id': idea_id,
            'message': f'Idea saved with ID: {idea_id}'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ideas/<int:idea_id>', methods=['GET'])
def api_get_idea(idea_id):
    """Get a single idea by ID"""
    idea = get_idea(idea_id)
    if idea:
        return jsonify({'success': True, 'data': idea})
    return jsonify({'success': False, 'error': 'Idea not found'}), 404


@app.route('/api/ideas/<int:idea_id>', methods=['PUT'])
def api_update_idea(idea_id):
    """Update an existing idea"""
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400

    try:
        success = update_idea(idea_id, **data)
        if success:
            return jsonify({'success': True, 'message': 'Idea updated'})
        return jsonify({'success': False, 'error': 'Idea not found or no changes'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ideas/<int:idea_id>', methods=['DELETE'])
def api_delete_idea(idea_id):
    """Delete an idea"""
    try:
        success = delete_idea(idea_id)
        if success:
            return jsonify({'success': True, 'message': 'Idea deleted'})
        return jsonify({'success': False, 'error': 'Idea not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/categories', methods=['GET'])
def api_get_categories():
    """Get all categories with counts"""
    categories = get_categories()
    return jsonify({'success': True, 'data': categories})


@app.route('/api/recent', methods=['GET'])
def api_get_recent():
    """Get recent ideas"""
    limit = request.args.get('limit', 10, type=int)
    ideas = get_recent_ideas(limit=limit)
    return jsonify({'success': True, 'data': ideas})


@app.route('/api/ideas/<int:idea_id>/relations', methods=['GET'])
def api_get_relations(idea_id):
    """Get relations for an idea"""
    relations = get_relations(idea_id)
    return jsonify({'success': True, 'data': relations})


@app.route('/api/relations', methods=['POST'])
def api_add_relation():
    """Add a relation between ideas"""
    data = request.get_json()

    if not data or not data.get('idea_id_1') or not data.get('idea_id_2'):
        return jsonify({'success': False, 'error': 'idea_id_1 and idea_id_2 are required'}), 400

    try:
        relation_id = add_relation(
            idea_id_1=data['idea_id_1'],
            idea_id_2=data['idea_id_2'],
            relation_type=data.get('relation_type', 'related'),
            note=data.get('note')
        )
        return jsonify({'success': True, 'id': relation_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/chat', methods=['POST'])
def api_chat():
    """Process chat messages - Core Agent interface"""
    data = request.get_json()

    if not data or not data.get('message'):
        return jsonify({'success': False, 'error': 'Message is required'}), 400

    message = data['message'].strip()

    # Handle quick commands
    if message.startswith('/'):
        return handle_command(message)

    # For now, return a simple response
    # This can be enhanced with actual AI processing later
    return jsonify({
        'success': True,
        'response': f'Received: {message}',
        'type': 'text'
    })


def handle_command(message):
    """Handle slash commands"""
    parts = message.split(maxsplit=1)
    command = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ''

    if command == '/add':
        if not args:
            return jsonify({
                'success': False,
                'error': 'Usage: /add <title> | <content>'
            })

        # Parse title | content format
        if '|' in args:
            title, content = args.split('|', 1)
            title = title.strip()
            content = content.strip()
        else:
            title = args[:50] + ('...' if len(args) > 50 else '')
            content = args

        idea_id = add_idea(title=title, content=content, source='chat')
        return jsonify({
            'success': True,
            'response': f'Added idea #{idea_id}: {title}',
            'type': 'action',
            'action': 'add',
            'idea_id': idea_id
        })

    elif command == '/search':
        if not args:
            return jsonify({
                'success': False,
                'error': 'Usage: /search <keyword>'
            })

        ideas = search_ideas(keyword=args, limit=10)
        return jsonify({
            'success': True,
            'response': f'Found {len(ideas)} ideas',
            'type': 'search',
            'data': ideas
        })

    elif command == '/recent':
        limit = int(args) if args.isdigit() else 5
        ideas = get_recent_ideas(limit=limit)
        return jsonify({
            'success': True,
            'response': f'Recent {len(ideas)} ideas',
            'type': 'list',
            'data': ideas
        })

    elif command == '/category':
        if not args:
            categories = get_categories()
            return jsonify({
                'success': True,
                'response': 'Categories',
                'type': 'categories',
                'data': categories
            })

        ideas = search_ideas(category=args, limit=20)
        return jsonify({
            'success': True,
            'response': f'Ideas in "{args}"',
            'type': 'list',
            'data': ideas
        })

    elif command == '/help':
        return jsonify({
            'success': True,
            'response': '''Available commands:
/add <content> - Quick add idea
/search <keyword> - Search ideas
/recent [n] - Show recent ideas
/category [name] - List categories or filter by category
/help - Show this help''',
            'type': 'help'
        })

    else:
        return jsonify({
            'success': False,
            'error': f'Unknown command: {command}. Try /help'
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
    # Ensure database exists
    if not DB_PATH.exists():
        init_database()

    print("Starting AgentNote Web UI...")
    print("Open http://localhost:5000 in your browser")
    app.run(host='0.0.0.0', port=5000, debug=True)
