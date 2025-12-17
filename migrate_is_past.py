from sqlalchemy import create_engine, text

engine = create_engine('sqlite:///bot_data.db', connect_args={'check_same_thread': False})

with engine.connect() as conn:
    # Проверяем структуру
    result = conn.execute(text('PRAGMA table_info(rentals)'))
    columns = [row[1] for row in result.fetchall()]
    print(f'Current columns: {columns}')
    
    # Добавляем is_past если её нет
    if 'is_past' not in columns:
        print('Adding is_past column...')
        conn.execute(text('ALTER TABLE rentals ADD COLUMN is_past BOOLEAN DEFAULT 0'))
        conn.commit()
        print('✅ Added is_past column')
    else:
        print('✅ is_past column already exists')
