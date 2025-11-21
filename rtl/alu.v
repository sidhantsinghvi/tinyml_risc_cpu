module alu (
    input  [31:0] a,
    input  [31:0] b,
    input  [3:0]  opcode,
    output reg [31:0] result
);
    wire signed [7:0] a_lane0 = a[7:0];
    wire signed [7:0] a_lane1 = a[15:8];
    wire signed [7:0] a_lane2 = a[23:16];
    wire signed [7:0] a_lane3 = a[31:24];

    wire signed [7:0] b_lane0 = b[7:0];
    wire signed [7:0] b_lane1 = b[15:8];
    wire signed [7:0] b_lane2 = b[23:16];
    wire signed [7:0] b_lane3 = b[31:24];

    wire signed [15:0] prod0 = a_lane0 * b_lane0;
    wire signed [15:0] prod1 = a_lane1 * b_lane1;
    wire signed [15:0] prod2 = a_lane2 * b_lane2;
    wire signed [15:0] prod3 = a_lane3 * b_lane3;

    wire signed [31:0] mac4_result = prod0 + prod1 + prod2 + prod3;
    wire signed [31:0] conv3_result = prod0 + prod1 + prod2;

    wire signed [31:0] signed_a = a;
    wire signed [31:0] sigmoid_shift = signed_a >>> 1;

    always @(*) begin
        case (opcode)
            4'b0000: result = a + b;      // add
            4'b0001: result = a - b;      // sub
            4'b0010: result = a & b;      // and
            4'b0011: result = a | b;      // or
            4'b0100: result = a ^ b;      // xor
            4'b1000: result = mac4_result;
            4'b1101: result = conv3_result;
            4'b1110: begin
                if (signed_a < -32'sd64) begin
                    result = 32'h0000_0080; // -128 clipped into low byte
                end else if (signed_a > 32'sd64) begin
                    result = 32'h0000_007F; // +127
                end else begin
                    result = {24'h0, sigmoid_shift[7:0]};
                end
            end
            4'b1111: result = a; // accumulator uses rs1 data, final value selected in top
            default: result = 32'h0000_0000;
        endcase
    end
endmodule
