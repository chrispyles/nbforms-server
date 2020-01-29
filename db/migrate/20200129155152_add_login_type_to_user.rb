class AddLoginTypeToUser < ActiveRecord::Migration[6.0]
  def change
    add_column :users, :oauth_required, :boolean
  end
end
