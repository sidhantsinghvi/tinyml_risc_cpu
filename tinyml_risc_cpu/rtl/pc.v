module pc (
    input         clk,
    input         rst,
    output reg [31:0] pc_out
);
    always @(posedge clk) begin
        if (rst) begin
            pc_out <= 32'h0000_0000;
        end else begin
            pc_out <= pc_out + 32'd4;
        end
    end
endmodule
