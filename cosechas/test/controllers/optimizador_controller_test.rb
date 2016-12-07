require 'test_helper'

class OptimizadorControllerTest < ActionDispatch::IntegrationTest
  test "should get index" do
    get optimizador_index_url
    assert_response :success
  end

end
