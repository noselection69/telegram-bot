import re

with open('bot/web/static/app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Найдем строку, где начинается функция loadItems
start_idx = None
end_idx = None

for i, line in enumerate(lines):
    if 'async function loadItems()' in line:
        start_idx = i
    if start_idx is not None and i > start_idx and line.strip() == '}' and not lines[i+1].strip().startswith('function'):
        end_idx = i
        break

if start_idx is not None and end_idx is not None:
    # Заменяем линии
    new_func = [
        'async function loadItems() {\n',
        '    // Вкладка "Ваши товары" больше не используется\n',
        '    // История продаж отображается в отдельной вкладке "История продаж"\n',
        '    // Все товары в наличии показываются в "Инвентарь"\n',
        '    \n',
        '    const itemsList = document.getElementById(\'itemsList\');\n',
        '    if (itemsList) {\n',
        '        itemsList.innerHTML = `\n',
        '            <div class="empty">\n',
        '                <p>📦 Используйте "Инвентарь" для товаров в наличии</p>\n',
        '                <p style="font-size: 12px; color: #bbb;">И "История продаж" для проданных товаров</p>\n',
        '            </div>\n',
        '        `;\n',
        '    }\n',
        '}\n',
    ]
    
    lines = lines[:start_idx] + new_func + lines[end_idx+1:]

with open('bot/web/static/app.js', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('✅ Файл обновлен')
