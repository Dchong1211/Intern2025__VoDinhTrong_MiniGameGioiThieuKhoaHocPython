            if isinstance(result, list):
                level_manager.run_code(result)
                code_panel.close()  # 🔒 đóng IDE khi code chạy