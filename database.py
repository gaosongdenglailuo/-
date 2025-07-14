import pymysql
from tkinter import messagebox

# 数据库连接配置
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "p1234",
    "database": "rushb",
    "charset": "utf8mb4"
}

def connect_db():
    """创建数据库连接"""
    return pymysql.connect(**DB_CONFIG)

def find_min_available_id():
    """查找最小可用的图书ID"""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        # 获取所有已使用的ID
        cursor.execute("SELECT id FROM book ORDER BY id")
        used_ids = [row[0] for row in cursor.fetchall()]
        
        # 如果没有记录，返回1
        if not used_ids:
            return 1
        
        # 查找最小可用ID
        min_id = 1
        for used_id in used_ids:
            if used_id > min_id:
                break
            min_id = used_id + 1
        
        return min_id
    except Exception as e:
        messagebox.showerror("错误", f"查找最小可用ID失败: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def add_book(bname, writer, book_id=None):
    """添加图书（可选指定ID）"""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        # 检查必填字段
        if not bname or not writer:
            return False, "添加失败: 书名和作者不能为空"
        
        # 如果未指定ID，查找最小可用ID
        if book_id is None:
            book_id = find_min_available_id()
            if book_id is None:
                return False, "无法确定可用ID"
        
        # 检查ID是否已存在
        cursor.execute("SELECT id FROM book WHERE id = %s", (book_id,))
        if cursor.fetchone():
            return False, f"添加失败: ID {book_id} 已存在"
        
        # 插入图书
        sql = "INSERT INTO book (id, bname, writer) VALUES (%s, %s, %s)"
        cursor.execute(sql, (book_id, bname, writer))
        
        conn.commit()
        return True, f"添加成功: ID={book_id} 《{bname}》- {writer}"
    except Exception as e:
        return False, f"添加失败: {e}"
    finally:
        cursor.close()
        conn.close()

def add_books_in_batch(book_list):
    """批量添加图书"""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        # 获取所有已使用的ID
        cursor.execute("SELECT id FROM book ORDER BY id")
        used_ids = {row[0] for row in cursor.fetchall()}
        
        # 查找最小可用ID
        min_id = 1
        if used_ids:
            sorted_ids = sorted(used_ids)
            for used_id in sorted_ids:
                if used_id > min_id:
                    break
                min_id = used_id + 1
        
        # 准备插入数据
        values = []
        for book in book_list:
            bname, writer = book
            # 如果书名或作者为空，跳过
            if not bname.strip() or not writer.strip():
                continue
            
            # 分配ID
            while min_id in used_ids:
                min_id += 1
            
            values.append((min_id, bname.strip(), writer.strip()))
            used_ids.add(min_id)
            min_id += 1
        
        if not values:
            return False, "没有有效的图书数据可添加"
        
        # 批量插入
        sql = "INSERT INTO book (id, bname, writer) VALUES (%s, %s, %s)"
        cursor.executemany(sql, values)
        
        conn.commit()
        return True, f"成功添加 {len(values)} 本图书"
    except Exception as e:
        conn.rollback()
        return False, f"批量添加失败: {e}"
    finally:
        cursor.close()
        conn.close()

def delete_book(book_id):
    """删除单本图书"""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        sql = "DELETE FROM book WHERE id = %s"
        cursor.execute(sql, (book_id,))
        conn.commit()
        return True, f"删除成功: ID={book_id}"
    except Exception as e:
        return False, f"删除失败: {e}"
    finally:
        cursor.close()
        conn.close()

def delete_books(book_ids):
    """批量删除图书"""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        # 构造IN查询的参数
        placeholders = ','.join(['%s'] * len(book_ids))
        sql = f"DELETE FROM book WHERE id IN ({placeholders})"
        cursor.execute(sql, book_ids)
        
        conn.commit()
        return True, f"成功删除 {cursor.rowcount} 本图书"
    except Exception as e:
        return False, f"批量删除失败: {e}"
    finally:
        cursor.close()
        conn.close()

def update_book(book_id, new_bname=None, new_writer=None, new_id=None):
    """更新图书（可选修改ID）"""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        # 检查新ID是否已存在（如果修改ID）
        if new_id is not None and new_id != book_id:
            cursor.execute("SELECT id FROM book WHERE id = %s", (new_id,))
            if cursor.fetchone():
                return False, f"更新失败: 新ID {new_id} 已存在"
        
        # 获取原图书信息
        cursor.execute("SELECT bname, writer FROM book WHERE id = %s", (book_id,))
        original_book = cursor.fetchone()
        if not original_book:
            return False, f"更新失败: 找不到ID为 {book_id} 的图书"
        
        # 使用原值或新值
        final_bname = new_bname if new_bname is not None and new_bname != "" else original_book[0]
        final_writer = new_writer if new_writer is not None and new_writer != "" else original_book[1]
        
        # 更新图书信息
        if new_id is None or new_id == book_id:
            sql = "UPDATE book SET bname=%s, writer=%s WHERE id=%s"
            cursor.execute(sql, (final_bname, final_writer, book_id))
        else:
            # 更新ID时需要同时更新借阅记录
            # 更新图书ID
            sql = "UPDATE book SET id=%s, bname=%s, writer=%s WHERE id=%s"
            cursor.execute(sql, (new_id, final_bname, final_writer, book_id))
            
            # 更新借阅记录中的book_id
            update_borrow = "UPDATE borrow_record SET book_id=%s WHERE book_id=%s"
            cursor.execute(update_borrow, (new_id, book_id))
        
        conn.commit()
        
        if new_id is None or new_id == book_id:
            return True, f"更新成功: ID={book_id}"
        else:
            return True, f"更新成功: 原ID={book_id} 新ID={new_id}"
    except Exception as e:
        return False, f"更新失败: {e}"
    finally:
        cursor.close()
        conn.close()

def search_books(keyword=""):
    """查询图书"""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        if keyword:
            # 尝试按ID搜索
            if keyword.isdigit():
                sql = "SELECT * FROM book WHERE id = %s"
                cursor.execute(sql, (int(keyword),))
            else:
                sql = "SELECT * FROM book WHERE bname LIKE %s OR writer LIKE %s"
                cursor.execute(sql, (f"%{keyword}%", f"%{keyword}%"))
        else:
            cursor.execute("SELECT * FROM book")
        
        books = cursor.fetchall()
        return True, books
    except Exception as e:
        return False, f"查询失败: {e}"
    finally:
        cursor.close()
        conn.close()

def initialize_database():
    """初始化数据库表结构（添加级联更新）"""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        # 创建图书表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS book (
            id INT AUTO_INCREMENT PRIMARY KEY,
            bname VARCHAR(255) NOT NULL,
            writer VARCHAR(255) NOT NULL
        )
        """)
        
        # 创建借阅记录表（添加级联更新）
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS borrow_record (
            id INT AUTO_INCREMENT PRIMARY KEY,
            book_id INT NOT NULL,
            borrower VARCHAR(100) NOT NULL,
            borrow_date DATE NOT NULL,
            return_date DATE,
            FOREIGN KEY (book_id) REFERENCES book(id) ON UPDATE CASCADE
        )
        """)
        
        conn.commit()
        return True, "数据库初始化成功"
    except Exception as e:
        return False, f"数据库初始化失败: {e}"
    finally:
        cursor.close()
        conn.close()