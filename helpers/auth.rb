require 'oauth2'

GOOGLE_API_SCOPES = ['profile','email'].join(' ')


def auth_client
  @auth_client ||= OAuth2::Client.new(ENV['GOOGLE_KEY'], ENV['GOOGLE_SECRET'], {
      :site => 'https://accounts.google.com',
      :authorize_url => "/o/oauth2/auth",
      :token_url => "/o/oauth2/token"
  })
end

def auth_token_wrapper
  OAuth2::AccessToken.new(auth_client,
                          @new_token.token,
                          {
                              :refresh_token => @new_token.refresh_token,
                              :header_format => 'Bearer %s'
                          }
  )
end

def auth_process_code(code)
  @new_token = auth_client.auth_code.get_token(code, :redirect_uri => auth_callback_full_url)
  @user_info = auth_token_wrapper.get("https://www.googleapis.com/oauth2/v3/userinfo").parsed
  user = User.first_or_initialize name: @user_info['name'], email: @user_info['email']
  user.save!
  return user
end

def auth_callback_path
  '/auth/callback'
end

def auth_logout_path
  '/logout'
end

def auth_callback_full_url
  "#{request.base_url}#{auth_callback_path}"
end

def auth_authorize_link
  auth_client.auth_code.authorize_url({
      :redirect_uri => auth_callback_full_url,
      :scope => GOOGLE_API_SCOPES,
      :access_type => "offline"
  })
end
