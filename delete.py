from app import app, db, User, Post, PostLike

def delete_all_data():
    """Delete all data from the database"""
    try:
        with app.app_context():
            # Delete in order due to foreign key constraints
            # First delete post likes
            deleted_likes = PostLike.query.delete()
            print(f"Deleted {deleted_likes} post likes")
            
            # Then delete posts
            deleted_posts = Post.query.delete()
            print(f"Deleted {deleted_posts} posts")
            
            # Finally delete users
            deleted_users = User.query.delete()
            print(f"Deleted {deleted_users} users")
            
            # Commit the changes
            db.session.commit()
            print("All data deleted successfully!")
            
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting data: {e}")

if __name__ == '__main__':
    # Confirmation prompt
    confirmation = input("Are you sure you want to delete ALL data? Type 'DELETE ALL' to confirm: ")
    
    if confirmation == 'DELETE ALL':
        delete_all_data()
    else:
        print("Operation cancelled.")